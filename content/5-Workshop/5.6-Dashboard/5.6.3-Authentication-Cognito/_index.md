---
title : "Authentication with Amazon Cognito"
date : 2024-01-01
weight : 3
chapter : false
pre : " <b> 5.6.3 </b> "
---

In this section, we will protect the CloudCost Insight Dashboard using **Amazon Cognito**. After completion, only authenticated users will be able to call **API Gateway** to view AWS cost data.

### Authentication Architecture

The authentication flow works as follows:

1. The user accesses the **CloudFront Dashboard**.
2. **Cognito** returns the login page (managed UI).
3. The user enters their username/password -> **Cognito** authenticates.
4. **Cognito** issues **JWTs** (ID Token, Access Token).
5. The Dashboard calls **API Gateway** with the **JWT**.
6. **API Gateway** validates the JWT -> **Lambda** reads cost data from **S3**.

The frontend uses **Authorization Code Flow with PKCE**. This mechanism is suitable for browser-based applications because it does not require storing a client secret in JavaScript.

### Objectives

- Create an **Amazon Cognito User Pool** to manage users.
- Create an **App Client** for the Web Dashboard.
- Create a **Cognito Domain** to provide the login page.
- Integrate **Cognito** into the Frontend.
- Configure an **API Gateway JWT Authorizer**.
- Allow only valid access tokens to call **GET /costs**.

**CORS** only restricts where a browser is allowed to call an API; it does not prevent someone from calling the API using **curl/Postman**. Therefore, we will restrict **CORS** and add **JWT authentication** with **Cognito**.

### Restrict CORS to the exact CloudFront Dashboard

Open the `terraform/api_gateway.tf` file, find and replace the following code:

```hcl
allow_origins = ["*"]
```
Change it to:

```hcl
allow_origins = ["https://${aws_cloudfront_distribution.web.domain_name}"]
allow_methods = ["GET", "OPTIONS"]
allow_headers = ["Content-Type", "Authorization"]
```

The configuration above tightens CORS security for API Gateway. It allows only the project's **CloudFront** domain to call the API, limits access to read-only operations (**GET**), and allows the frontend to include an authentication token through the **Authorization** header.

### Create Cognito User Pool

We will create the `terraform/cognito.tf` file:

```hcl
resource "aws_cognito_user_pool" "dashboard" {
  name = "${var.project_name}-dashboard-users"

  # Configure login using email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Apply strong password policy
  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }
}

resource "aws_cognito_user_pool_client" "dashboard" {
  # Create App Client for the Frontend to communicate with Cognito
  name         = "${var.project_name}-dashboard-web"
  user_pool_id = aws_cognito_user_pool.dashboard.id

  generate_secret = false # Do not use a Secret key

  # Enable necessary secure authentication flows
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]
}
```

### Attach the JWT authorizer to the API route

**1.** Open the `terraform/api_gateway.tf` file and add the following code:

```hcl
# Configure JWT Authorizer for API Gateway to authenticate users with AWS Cognito
resource "aws_apigatewayv2_authorizer" "dashboard_jwt" {
  api_id          = aws_apigatewayv2_api.dashboard.id
  name            = "${var.project_name}-jwt"
  authorizer_type = "JWT"

  # Specify where API Gateway will extract the token from the request (from the "Authorization" Header)
  identity_sources = [
    "$request.header.Authorization"
  ]

  # Detailed JWT configuration so API Gateway knows how to verify the token's validity
  jwt_configuration {
    # The token must be issued for this Client ID (Cognito App Client)
    audience = [aws_cognito_user_pool_client.dashboard.id]

    # The URL of the token issuer (the project's Cognito User Pool)
    issuer = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.dashboard.id}"
  }
}
```

Update the `aws_apigatewayv2_route.costs` resource:

```hcl
# Requests calling "GET /costs" must have a valid JWT
resource "aws_apigatewayv2_route" "costs" {
  api_id             = aws_apigatewayv2_api.dashboard.id
  route_key          = "GET /costs"
  target             = "integrations/${aws_apigatewayv2_integration.api.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.dashboard_jwt.id
}
```

Now, **API Gateway** will only forward requests to Lambda when the Cognito token is valid.

**2.** Update output in the `terraform/outputs.tf` file:

```hcl
output "user_pool_id" {
  value = aws_cognito_user_pool.dashboard.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.dashboard.id
}

output "cognito_hosted_ui_url" {
  description = "Cognito Hosted UI sign-in endpoint for the dashboard"
  value       = "https://${aws_cognito_user_pool_domain.dashboard.domain}.auth.${var.aws_region}.amazoncognito.com/login"
}
```

### Create Cognito Domain

To use the Cognito Hosted UI, we need to register a unique domain name. This domain will be the redirection destination when users click the **Sign In** button.

Open the file `terraform/cognito.tf` and update `resource "aws_cognito_user_pool_client.dashboard"` as follows:

```hcl
resource "aws_cognito_user_pool_client" "dashboard" {
  name         = "${var.project_name}-dashboard-web"
  user_pool_id = aws_cognito_user_pool.dashboard.id

  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]

  # Hosted UI uses OAuth authorization-code flow. Public browser clients
  # don't have a client secret; the frontend generates a PKCE verifier for each login.
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls = [
    "https://${aws_cloudfront_distribution.web.domain_name}/"
  ]
  logout_urls = [
    "https://${aws_cloudfront_distribution.web.domain_name}/"
  ]
}

# Amazon Cognito managed login (Hosted UI) domain.
resource "aws_cognito_user_pool_domain" "dashboard" {
  domain       = "${var.project_name}-${data.aws_caller_identity.current.account_id}"
  user_pool_id = aws_cognito_user_pool.dashboard.id
}
```

### Integrate authentication into the Web Dashboard

To allow the Frontend to automatically redirect users to the **Cognito** login page and attach the Token when calling APIs, we need to update the `terraform/web_hosting.tf` file and modify the `local` block as follows for Terraform to inject these variables into `script.js`:

```hcl
# upload script.js to S3
locals {
  rendered_script = replace(
    replace(
      replace(
        file("${path.module}/web/script.js"),
        "REPLACE_MY_API_ENDPOINT",
        "${trim(aws_apigatewayv2_stage.default.invoke_url, "/")}/costs"
      ),
      "REPLACE_MY_COGNITO_DOMAIN",
      "https://${aws_cognito_user_pool_domain.dashboard.domain}.auth.${var.aws_region}.amazoncognito.com"
    ),
    "REPLACE_MY_COGNITO_CLIENT_ID",
    aws_cognito_user_pool_client.dashboard.id
  )
}
```

Open the `index.html` file and add **Sign in** and **Sign out** buttons to the Web page:

```html
<button id="login-button">Sign in</button>
<button id="logout-button" style="display:none;">Sign out</button>
```

The exact content of the `index.html` file is as follows:

```html
<!DOCTYPE html>
<html lang="vi">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CloudCost Insight — Dashboard</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="style.css" />
</head>

<body>
    <header>
        <div>
            <h1>☁️ CloudCost Insight</h1>
            <p id="header-subtitle">AWS Cost Monitoring &amp; Alert Dashboard — Near Real-Time</p>
        </div>
        <div class="header-controls">
            <button id="login-button">Sign in</button>
            <button id="logout-button" style="display:none;">Sign out</button>
            <button id="lang-toggle">🇻🇳 VI</button>
            <button id="theme-toggle">🌙</button>
        </div>
    </header>

    <div id="status" class="status">Loading cost data...</div>

    <div id="content" style="display:none;">
        <!-- KPI -->
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="label" id="label-total">Total Cost (Period)</div>
                <div class="value" id="kpi-total">$0.00</div>
            </div>
            <div class="kpi-card">
                <div class="label" id="label-threshold">Alert Threshold/Day</div>
                <div class="value" id="kpi-threshold">$0.00</div>
            </div>
            <div class="kpi-card">
                <div class="label" id="label-days">Monitored Days</div>
                <div class="value" id="kpi-days">0</div>
            </div>
            <div class="kpi-card">
                <div class="label" id="label-anomalies">Anomalous Days</div>
                <div class="value danger" id="kpi-anomalies">0</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="chart-grid">
            <div class="chart-card full-width">
                <h3 id="title-trend">📈 Daily Cost Trend (Threshold Line + Anomaly Markers)</h3>
                <canvas id="trendChart" height="90"></canvas>
            </div>
            <div class="chart-card">
                <h3 id="title-service">🍩 Cost Share by Service</h3>
                <div class="chart-small">
                    <canvas id="serviceChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3 id="title-top">📊 Top Cost Services</h3>
                <canvas id="topChart"></canvas>
            </div>
        </div>
    </div>

    <!-- JavaScript riêng -->
    <script src="script.js"></script>
</body>

</html>
```

Update CSS for the **Sign in** and **Sign out** buttons as follows:

```css
#login-button,
#logout-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
}
```

Then, update the `scripts.js` file with the exact content as follows:

```JavaScript
const API_ENDPOINT = "REPLACE_MY_API_ENDPOINT";

const COGNITO_DOMAIN = "REPLACE_MY_COGNITO_DOMAIN";
const COGNITO_CLIENT_ID = "REPLACE_MY_COGNITO_CLIENT_ID";
const REDIRECT_URI = window.location.origin + "/";

const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");

function base64Url(bytes) {
    let value = "";
    bytes.forEach((byte) => { value += String.fromCharCode(byte); });
    return btoa(value).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function randomValue(size = 32) {
    const bytes = new Uint8Array(size);
    crypto.getRandomValues(bytes);
    return base64Url(bytes);
}

async function createCodeChallenge(verifier) {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
    return base64Url(new Uint8Array(digest));
}

async function signIn() {
    const verifier = randomValue(64);
    const state = randomValue(32);
    const challenge = await createCodeChallenge(verifier);
    sessionStorage.setItem("pkce_verifier", verifier);
    sessionStorage.setItem("oauth_state", state);

    const params = new URLSearchParams({
        response_type: "code",
        client_id: COGNITO_CLIENT_ID,
        redirect_uri: REDIRECT_URI,
        scope: "openid email profile",
        state,
        code_challenge_method: "S256",
        code_challenge: challenge,
    });
    window.location.assign(COGNITO_DOMAIN + "/oauth2/authorize?" + params.toString());
}

async function exchangeAuthorizationCode(code) {
    const verifier = sessionStorage.getItem("pkce_verifier");
    if (!verifier) throw new Error("Login session expired. Please sign in again.");

    const body = new URLSearchParams({
        grant_type: "authorization_code",
        client_id: COGNITO_CLIENT_ID,
        code,
        redirect_uri: REDIRECT_URI,
        code_verifier: verifier,
    });
    const response = await fetch(COGNITO_DOMAIN + "/oauth2/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
    });
    const tokens = await response.json();
    if (!response.ok) throw new Error(tokens.error_description || tokens.error || "Token exchange failed");

    sessionStorage.setItem("id_token", tokens.id_token);
    sessionStorage.removeItem("pkce_verifier");
    sessionStorage.removeItem("oauth_state");
    return tokens.id_token;
}

async function getAuthenticatedToken() {
    const url = new URL(window.location.href);
    const code = url.searchParams.get("code");
    if (!code) return sessionStorage.getItem("id_token");

    const expectedState = sessionStorage.getItem("oauth_state");
    if (!expectedState || url.searchParams.get("state") !== expectedState) {
        throw new Error("Invalid login state. Please sign in again.");
    }

    const token = await exchangeAuthorizationCode(code);
    window.history.replaceState({}, document.title, REDIRECT_URI);
    return token;
}

function showAuthenticationState(isAuthenticated) {
    loginButton.style.display = isAuthenticated ? "none" : "inline-block";
    logoutButton.style.display = isAuthenticated ? "inline-block" : "none";
}

function signOut() {
    sessionStorage.removeItem("id_token");
    sessionStorage.removeItem("pkce_verifier");
    sessionStorage.removeItem("oauth_state");
    const params = new URLSearchParams({ client_id: COGNITO_CLIENT_ID, logout_uri: REDIRECT_URI });
    window.location.assign(COGNITO_DOMAIN + "/logout?" + params.toString());
}

// EN/VI
const translations = {
    en: {
        subtitle: "AWS Cost Monitoring & Alert Dashboard — Near Real-Time",
        labelTotal: "Total Cost (Period)",
        labelThreshold: "Alert Threshold/Day",
        labelDays: "Monitored Days",
        labelAnomalies: "Anomalous Days",
        titleTrend: "📈 Daily Cost Trend (Threshold Line + Anomaly Markers)",
        titleService: "🍩 Cost Share by Service",
        titleTop: "📊 Top Cost Services",
        loading: "Loading cost data...",
        dailyCost: "Daily Cost",
        budgetThreshold: "Budget Threshold",
        cost: "Cost ($)",
        error: "Error loading data: ",
        signIn: "Sign in",
        signOut: "Sign out",
        authenticationRequired: "Please sign in to view cost data.",
    },
    vi: {
        subtitle: "Bảng giám sát & cảnh báo chi phí AWS — Thời gian gần thực",
        labelTotal: "Tổng chi phí (kỳ)",
        labelThreshold: "Ngưỡng cảnh báo/ngày",
        labelDays: "Số ngày theo dõi",
        labelAnomalies: "Số ngày bất thường",
        titleTrend: "📈 Xu hướng chi phí theo ngày (đường ngưỡng + đánh dấu bất thường)",
        titleService: "🍩 Tỷ trọng theo dịch vụ",
        titleTop: "📊 Top dịch vụ tốn chi phí",
        loading: "Đang tải dữ liệu chi phí...",
        dailyCost: "Chi phí/ngày",
        budgetThreshold: "Ngưỡng ngân sách",
        cost: "Chi phí ($)",
        error: "Lỗi tải dữ liệu: ",
        signIn: "Đăng nhập",
        signOut: "Đăng xuất",
        authenticationRequired: "Vui lòng đăng nhập để xem dữ liệu chi phí.",
    },
};

// Current language
let currentLang = "en";
let latestData = null;
let charts = {};

// Colors by status
const statusColor = (s) =>
    s === "CRITICAL" ? "#e53e3e" : s === "WARNING" ? "#dd6b20" : "#38a169";

// Apply language to static labels (non-chart)
function applyStaticText() {
    const t = translations[currentLang];
    document.getElementById("header-subtitle").textContent = t.subtitle;
    document.getElementById("label-total").textContent = t.labelTotal;
    document.getElementById("label-threshold").textContent = t.labelThreshold;
    document.getElementById("label-days").textContent = t.labelDays;
    document.getElementById("label-anomalies").textContent = t.labelAnomalies;
    document.getElementById("title-trend").textContent = t.titleTrend;
    document.getElementById("title-service").textContent = t.titleService;
    document.getElementById("title-top").textContent = t.titleTop;
    loginButton.textContent = t.signIn;
    logoutButton.textContent = t.signOut;

    const status = document.getElementById("status");
    if (status.dataset.translationKey === "authenticationRequired") {
        status.textContent = t.authenticationRequired;
    }
}

// Re-render charts based on language
function renderCharts(data) {
    const t = translations[currentLang];

    Object.values(charts).forEach(c => c && c.destroy());

    const labels = data.daily_costs.map(d => d.date);
    const totals = data.daily_costs.map(d => d.total);
    const colors = data.daily_costs.map(d => statusColor(d.status));
    const threshold = Number(data.threshold);

    // Trend chart
    charts.trend = new Chart(document.getElementById("trendChart"), {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: t.dailyCost,
                    data: totals,
                    borderColor: "#3182ce",
                    backgroundColor: "rgba(49,130,206,0.1)",
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: colors,
                    pointRadius: 5,
                },
                {
                    label: t.budgetThreshold,
                    data: labels.map(() => threshold),
                    borderColor: "#e53e3e",
                    borderDash: [6, 4],
                    pointRadius: 0,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "top" },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.dataset.label || "";
                            let value = context.parsed.y;
                            if (value === null || value === undefined) value = context.parsed;
                            return label + ": $" + Number(value).toFixed(2);
                        }
                    }
                }
            }
        },
    });

    // Donut chart
    charts.service = new Chart(document.getElementById("serviceChart"), {
        type: "doughnut",
        data: {
            labels: data.top_services.map(s => s.service),
            datasets: [{
                data: data.top_services.map(s => s.cost),
                backgroundColor: ["#ff9900", "#3182ce", "#38a169", "#e53e3e", "#805ad5", "#dd6b20", "#00a4a6", "#d53f8c", "#718096", "#2b6cb0"],
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return (context.label || "") + ": $" + context.parsed.toFixed(2);
                        }
                    }
                }
            }
        },
    });

    // Top services chart
    charts.top = new Chart(document.getElementById("topChart"), {
        type: "bar",
        data: {
            labels: data.top_services.map(s => s.service),
            datasets: [{
                label: t.cost,
                data: data.top_services.map(s => s.cost),
                backgroundColor: "#ff9900",
            }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.dataset.label || "";
                            let value = context.parsed.x;
                            if (value === null || value === undefined) value = context.parsed;
                            return label + ": $" + Number(value).toFixed(2);
                        }
                    }
                }
            }
        },
    });
}

async function loadDashboard(idToken) {
    try {
        const res = await fetch(API_ENDPOINT, { headers: { Authorization: "Bearer " + idToken } });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        latestData = data;

        document.getElementById("status").style.display = "none";
        document.getElementById("content").style.display = "block";

        // KPI
        document.getElementById("kpi-total").textContent = "$" + data.grand_total.toFixed(2);
        document.getElementById("kpi-threshold").textContent = "$" + Number(data.threshold).toFixed(2);
        document.getElementById("kpi-days").textContent = data.days_count;
        const anomalies = data.daily_costs.filter(d => d.status !== "NORMAL").length;
        document.getElementById("kpi-anomalies").textContent = anomalies;

        applyStaticText();
        renderCharts(data);

    } catch (err) {
        document.getElementById("status").textContent =
            "❌ " + translations[currentLang].error + err.message;
    }
}

// Language toggle button
const langToggle = document.getElementById("lang-toggle");
langToggle.addEventListener("click", () => {
    currentLang = currentLang === "vi" ? "en" : "vi";
    langToggle.textContent = currentLang === "vi" ? "VI" : "EN";
    applyStaticText();
    if (latestData) renderCharts(latestData); // re-render charts with new language labels
});

// Dark mode button
const themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    themeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
    Chart.defaults.color = document.body.classList.contains("dark-mode") ? "#ffffff" : "#666";
    Object.values(charts).forEach(c => c && c.update());
});

// Initialize dashboard after Cognito returns a valid JWT.
async function initializeDashboard() {
    applyStaticText();
    try {
        const token = await getAuthenticatedToken();
        showAuthenticationState(Boolean(token));
        if (!token) {
            const status = document.getElementById("status");
            status.dataset.translationKey = "authenticationRequired";
            status.textContent = translations[currentLang].authenticationRequired;
            return;
        }
        await loadDashboard(token);
    } catch (err) {
        sessionStorage.removeItem("id_token");
        showAuthenticationState(false);
        document.getElementById("status").textContent = "Authentication error: " + err.message;
    }
}

loginButton.addEventListener("click", signIn);
logoutButton.addEventListener("click", signOut);
initializeDashboard();
```

Here, we have completed setting up the security authentication mechanism with **Amazon Cognito** for the Web Dashboard. We need to redeploy via the command line:

```bash
terraform apply
```

### Next steps

- [System Testing](5-Workshop/5.7-Testing/)
