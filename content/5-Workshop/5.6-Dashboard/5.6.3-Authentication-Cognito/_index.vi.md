---
title : "Xác thực với Amazon Cognito"
date : 2024-01-01
weight : 3
chapter : false
pre : " <b> 5.6.3 </b> "
---

Trong phần này, chúng ta sẽ bảo vệ CloudCost Insight Dashboard bằng **Amazon Cognito**. Sau khi hoàn thành, chỉ người dùng đã đăng nhập mới có thể gọi **API Gateway** để xem dữ liệu chi phí AWS.

### Kiến trúc xác thực

Luồng xác thực hoạt động như sau:

1. Người dùng đăng nhập Dashboard CloudFront.
2. **Cognito** trả về trang đăng nhập.
3. Người dùng nhập username/password -> **Cognito** xác thực.
4. **Cognito** cấp **JWT** (ID Token, Access Token).
5. Dashboard gọi **API Gateway** kèm **JWT**.
6. **API Gateway** hợp lệ JWT -> **Lambda đọc dữ liệu chi phí từ **S3**.

Frontend sử dụng **Authorization Code Flow với PKCE**. Đây là cơ chế phù hợp cho ứng dụng chạy trên trình duyệt vì không cần lưu client secret trong JavaScript.

### Mục tiêu

- Tạo **Amazon Cognito User Pool** để quản lý người dùng.
- Tạo **App Client** cho Web Dashboard.
- Tạo **Cognito Domain** cung cấp trang đăng nhập.
- Tích hợp **Cognito** vào Frontend.
- Cấu hình **API Gateway JWT Authorizer**.
- Chỉ cho phép access token hợp lệ gọi **GET /costs**.

**CORS** chỉ giới hạn nơi trình duyệt được phép gọi API, nó không ngăn ai đó gọi API bằng **curl/Postman**. Vì vậy, chúng ta sẽ giới hạn **CORS** và thêm **JWT authentication** bằng **Cognito**.

### Giới hạn CORS về đúng dashboard CloudFront

Mở file `terraform/api_gateway.tf`, tìm và thay đoạn code:

```hcl
allow_origins = ["*"]
```
Đổi thành:

```hcl
allow_origins = ["https://${aws_cloudfront_distribution.web.domain_name}"]
allow_methods = ["GET", "OPTIONS"]
allow_headers = ["Content-Type", "Authorization"]
```

Đoạn cấu hình trên nhằm siết chặt bảo mật CORS cho API Gateway. Nó chỉ cho phép duy nhất trên miền **CloudFront** của dự án được phép gọi API, giới hạn ở quyền đọc dữ liệu (**GET**), và cấp phép cho Frontend gửi kèm Token xác thực thông qua header **Authorization**.

### Tạo Cognito User Pool

Chúng ta sẽ tạo file `terraform/cognito.tf`:

```hcl
resource "aws_cognito_user_pool" "dashboard" {
  name = "${var.project_name}-dashboard-users"

  # Cấu hình đăng nhập bằng email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Áp dụng chính sách mật khẩu mạnh
  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }
}

resource "aws_cognito_user_pool_client" "dashboard" {
  # Tạo Client để Frontend giao tiếp với Cognito
  name         = "${var.project_name}-dashboard-web"
  user_pool_id = aws_cognito_user_pool.dashboard.id

  generate_secret = false # không dùng Secret key

  # Kích hoạt các luồng xác thực an toàn cần thiết
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]
}
```

### Gắn JWT authorizer vào route API

**1.** Mở file `terraform/api_gateway.tf` và thêm đoạn code sau:

```hcl
# Cấu hình JWT Authorizer cho API Gateway để xác thực người dùng bằng AWS Cognito
resource "aws_apigatewayv2_authorizer" "dashboard_jwt" {
  api_id          = aws_apigatewayv2_api.dashboard.id
  name            = "${var.project_name}-jwt"
  authorizer_type = "JWT"

  # Chỉ định vị trí API Gateway sẽ lấy token từ request (lấy từ Header "Authorization")
  identity_sources = [
    "$request.header.Authorization"
  ]

  # Cấu hình chi tiết về JWT để API Gateway biết cách xác minh tính hợp lệ của token
  jwt_configuration {
    # Token phải được cấp phát cho Client ID này (Cognito App Client)
    audience = [aws_cognito_user_pool_client.dashboard.id]

    # URL của tổ chức phát hành token (chính là Cognito User Pool của dự án)
    issuer = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.dashboard.id}"
  }
}
```

Cập nhật resource `aws_apigatewayv2_route.costs`:

```hcl
# Request gọi "GET /costs" phải có JWT hợp lệ
resource "aws_apigatewayv2_route" "costs" {
  api_id             = aws_apigatewayv2_api.dashboard.id
  route_key          = "GET /costs"
  target             = "integrations/${aws_apigatewayv2_integration.api.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.dashboard_jwt.id
}
```

Lúc này **API Gateway** chỉ chuyển request đến Lambda khi token Cognito hợp lệ.

**2.** Cập nhật output trong file `terraform/outputs.tf`:

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

### Tạo Cognito Domain

Để sử dụng được giao diện đăng nhập sẵn có (Hosted UI) của Cognito, chúng ta cần đăng ký một tên miền duy nhất. Tên miền này sẽ là nơi chuyển hướng người dùng khi họ nhấn nút **Đăng nhập**.

Mở file `terraform/cognito.tf` và cập nhật `resource "aws_cognito_user_pool_client.dashboard"` như sau:

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

  # Hosted UI sử dụng OAuth authorization-code flow. Public browser client
  # không có client secret; frontend tạo PKCE verifier cho mỗi lần đăng nhập.
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

### Tích hợp xác thực vào Web Dashboard

Để Frontend có thể tự động chuyển hướng người dùng đến trang đăng nhập **Cognito** và đính kèm Token khi gọi API, chúng ta cần cập nhật file `terraform/web_hosting.tf` và sửa lại khối `locals` như sau để Terraform chèn các biến này vào `script.js`:

```hcl
# upload script.js lên S3
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

Mở file `index.html` và thêm nút **Sign in** và **Sign out** cho trang Web:

```html
<button id="login-button">Sign in</button>
<button id="logout-button" style="display:none;">Sign out</button>
```

Nội dung chính xác của file `index.html` như sau:

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
            <p id="header-subtitle">AWS Cost Monitoring &amp; Alert Dashboard</p>
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

        <div class="chart-grid">
            <div class="chart-card full-width">
                <h3 id="title-trend">📈 Daily Cost Trend (Threshold Line + Anomaly Markers)</h3>
                <canvas id="trendChart" height="90"></canvas>
            </div>

            <div class="chart-card">
                <h3 id="title-alert">🚨 Alert History</h3>
                <div id="alert-history" class="alert-history"></div>
            </div>

            <div class="chart-card">
                <h3 id="title-top">📊 Top Cost Services</h3>
                <canvas id="topChart"></canvas>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
</body>

</html>
```

Cập nhật CSS cho button **Sign in** và **Sign out**, bạn có thể làm như sau:

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

Nội dung của file `style.css` chính xác như sau:

```css
/* style.css — CloudCost Insight Dashboard */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --bg-color: #f0f2f5;
    --text-color: #1a202c;
    --card-bg: #fff;
    --label-color: #718096;
    --heading-color: #2d3748;
    --border-color: #e2e8f0;
    --table-head-bg: #f7fafc;
    --shadow-color: rgba(0, 0, 0, 0.08);
    --header-bg: linear-gradient(135deg, #232f3e, #ff9900);
}

body.dark-mode {
    --bg-color: #1a202c;
    --text-color: #ffffff;
    --card-bg: #2d3748;
    --label-color: #a0aec0;
    --heading-color: #ffffff;
    --border-color: #4a5568;
    --table-head-bg: #374151;
    --shadow-color: rgba(0, 0, 0, 0.3);
}

body {
    font-family: "Segoe UI", Arial, sans-serif;
    background: var(--bg-color);
    color: var(--text-color);
    padding: 24px;
    transition: background 0.3s, color 0.3s;
}

header {
    background: var(--header-bg);
    color: #fff;
    padding: 20px 28px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

#theme-toggle,
#lang-toggle,
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

#theme-toggle:hover,
#lang-toggle:hover,
#login-button:hover,
#logout-button:hover {
    background: rgba(255, 255, 255, 0.3);
}

header h1 {
    font-size: 24px;
}

header p {
    opacity: 0.9;
    font-size: 14px;
    margin-top: 4px;
}

.kpi-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}

.kpi-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px 24px;
    flex: 1;
    min-width: 200px;
    box-shadow: 0 1px 4px var(--shadow-color);
    transition: background 0.3s, box-shadow 0.3s;
}

.kpi-card .label {
    font-size: 13px;
    color: var(--label-color);
}

.kpi-card .value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 6px;
}

.kpi-card .value.danger {
    color: #e53e3e;
}

.chart-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

.chart-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 4px var(--shadow-color);
    transition: background 0.3s, box-shadow 0.3s;
}

.chart-card h3 {
    font-size: 16px;
    margin-bottom: 16px;
    color: var(--heading-color);
}

.full-width {
    grid-column: 1 / -1;
}

.alert-history {
    min-height: 250px;
}

.table-wrapper {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th,
td {
    padding: 12px 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    color: var(--label-color);
    background: var(--table-head-bg);
    font-size: 12px;
    text-transform: uppercase;
}

.status-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
}

.status-badge.warning {
    background: #dd6b20;
}

.status-badge.critical {
    background: #e53e3e;
}

.no-alerts {
    color: #38a169;
    padding: 16px 0;
}

.status {
    text-align: center;
    padding: 40px;
    color: #718096;
}

@media (max-width: 900px) {
    body {
        padding: 16px;
    }

    header {
        padding: 18px;
        align-items: flex-start;
        flex-direction: column;
        gap: 16px;
    }

    .chart-grid {
        grid-template-columns: 1fr;
    }
}
```

Sau đó, cập nhật file `scripts.js` với chính xác nội dung như sau:

```JavaScript
const API_ENDPOINT = "REPLACE_MY_API_ENDPOINT";

const COGNITO_DOMAIN = "REPLACE_MY_COGNITO_DOMAIN";
const COGNITO_CLIENT_ID = "REPLACE_MY_COGNITO_CLIENT_ID";
const REDIRECT_URI = window.location.origin + "/";

const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");

function base64Url(bytes) {
    let value = "";
    bytes.forEach((byte) => {
        value += String.fromCharCode(byte);
    });

    return btoa(value)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/g, "");
}

function randomValue(size = 32) {
    const bytes = new Uint8Array(size);
    crypto.getRandomValues(bytes);
    return base64Url(bytes);
}

async function createCodeChallenge(verifier) {
    const digest = await crypto.subtle.digest(
        "SHA-256",
        new TextEncoder().encode(verifier),
    );

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

    window.location.assign(
        `${COGNITO_DOMAIN}/oauth2/authorize?${params.toString()}`,
    );
}

async function exchangeAuthorizationCode(code) {
    const verifier = sessionStorage.getItem("pkce_verifier");

    if (!verifier) {
        throw new Error("Login session expired. Please sign in again.");
    }

    const body = new URLSearchParams({
        grant_type: "authorization_code",
        client_id: COGNITO_CLIENT_ID,
        code,
        redirect_uri: REDIRECT_URI,
        code_verifier: verifier,
    });

    const response = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
    });

    const tokens = await response.json();

    if (!response.ok) {
        throw new Error(
            tokens.error_description || tokens.error || "Token exchange failed",
        );
    }

    sessionStorage.setItem("id_token", tokens.id_token);
    sessionStorage.removeItem("pkce_verifier");
    sessionStorage.removeItem("oauth_state");

    return tokens.id_token;
}

async function getAuthenticatedToken() {
    const url = new URL(window.location.href);
    const code = url.searchParams.get("code");

    if (!code) {
        return sessionStorage.getItem("id_token");
    }

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

    const params = new URLSearchParams({
        client_id: COGNITO_CLIENT_ID,
        logout_uri: REDIRECT_URI,
    });

    window.location.assign(`${COGNITO_DOMAIN}/logout?${params.toString()}`);
}

// EN/VI
const translations = {
    en: {
        subtitle: "AWS Cost Monitoring & Alert Dashboard",
        labelTotal: "Total Cost (Period)",
        labelThreshold: "Alert Threshold/Day",
        labelDays: "Monitored Days",
        labelAnomalies: "Anomalous Days",
        titleTrend: "📈 Daily Cost Trend (Threshold Line + Anomaly Markers)",
        titleAlert: "🚨 Alert History",
        titleTop: "📊 Top Cost Services",
        dailyCost: "Daily Cost",
        budgetThreshold: "Budget Threshold",
        cost: "Cost ($)",
        date: "Date",
        status: "Status",
        reason: "Reason",
        warningReason: "Budget threshold exceeded",
        criticalReason: "Cost spike detected",
        noAlerts: "No abnormal cost days were detected.",
        error: "Error loading data: ",
        signIn: "Sign in",
        signOut: "Sign out",
        authenticationRequired: "Please sign in to view cost data.",
    },
    vi: {
        subtitle: "Bảng giám sát & cảnh báo chi phí AWS",
        labelTotal: "Tổng chi phí (kỳ)",
        labelThreshold: "Ngưỡng cảnh báo/ngày",
        labelDays: "Số ngày theo dõi",
        labelAnomalies: "Số ngày bất thường",
        titleTrend: "📈 Xu hướng chi phí theo ngày (đường ngưỡng + đánh dấu bất thường)",
        titleAlert: "🚨 Lịch sử cảnh báo",
        titleTop: "📊 Top dịch vụ tốn chi phí",
        dailyCost: "Chi phí/ngày",
        budgetThreshold: "Ngưỡng ngân sách",
        cost: "Chi phí ($)",
        date: "Ngày",
        status: "Trạng thái",
        reason: "Lý do",
        warningReason: "Vượt ngưỡng ngân sách",
        criticalReason: "Phát hiện chi phí tăng đột biến",
        noAlerts: "Không phát hiện ngày có chi phí bất thường.",
        error: "Lỗi tải dữ liệu: ",
        signIn: "Đăng nhập",
        signOut: "Đăng xuất",
        authenticationRequired: "Vui lòng đăng nhập để xem dữ liệu chi phí.",
    },
};

let currentLang = "en";
let latestData = null;
let charts = {};

const statusColor = (status) =>
    status === "CRITICAL"
        ? "#e53e3e"
        : status === "WARNING"
            ? "#dd6b20"
            : "#38a169";

function applyStaticText() {
    const t = translations[currentLang];

    document.getElementById("header-subtitle").textContent = t.subtitle;
    document.getElementById("label-total").textContent = t.labelTotal;
    document.getElementById("label-threshold").textContent = t.labelThreshold;
    document.getElementById("label-days").textContent = t.labelDays;
    document.getElementById("label-anomalies").textContent = t.labelAnomalies;
    document.getElementById("title-trend").textContent = t.titleTrend;
    document.getElementById("title-alert").textContent = t.titleAlert;
    document.getElementById("title-top").textContent = t.titleTop;
    loginButton.textContent = t.signIn;
    logoutButton.textContent = t.signOut;

    const status = document.getElementById("status");

    if (status.dataset.translationKey === "authenticationRequired") {
        status.textContent = t.authenticationRequired;
    }
}

function renderCharts(data) {
    const t = translations[currentLang];

    Object.values(charts).forEach((chart) => chart && chart.destroy());
    charts = {};

    const labels = data.daily_costs.map((day) => day.date);
    const totals = data.daily_costs.map((day) => day.total);
    const colors = data.daily_costs.map((day) => statusColor(day.status));
    const threshold = Number(data.threshold);

    charts.trend = new Chart(document.getElementById("trendChart"), {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: t.dailyCost,
                    data: totals,
                    borderColor: "#3182ce",
                    backgroundColor: "rgba(49, 130, 206, 0.1)",
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
                legend: {
                    position: "top",
                },
                tooltip: {
                    callbacks: {
                        label(context) {
                            const label = context.dataset.label || "";
                            return `${label}: $${Number(context.parsed.y).toFixed(2)}`;
                        },
                    },
                },
            },
        },
    });

    charts.top = new Chart(document.getElementById("topChart"), {
        type: "bar",
        data: {
            labels: data.top_services.map((service) => service.service),
            datasets: [
                {
                    label: t.cost,
                    data: data.top_services.map((service) => service.cost),
                    backgroundColor: "#ff9900",
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label(context) {
                            return `${t.cost}: $${Number(context.parsed.x).toFixed(2)}`;
                        },
                    },
                },
            },
        },
    });
}

function renderAlertHistory(data) {
    const t = translations[currentLang];
    const container = document.getElementById("alert-history");

    const anomalies = data.daily_costs.filter(
        (day) => day.status !== "NORMAL",
    );

    if (anomalies.length === 0) {
        container.innerHTML = `<p class="no-alerts">✅ ${t.noAlerts}</p>`;
        return;
    }

    const rows = anomalies
        .slice()
        .reverse()
        .map((day) => {
            const reason =
                day.status === "CRITICAL"
                    ? t.criticalReason
                    : t.warningReason;

            return `
                <tr>
                    <td>${day.date}</td>
                    <td>$${Number(day.total).toFixed(2)}</td>
                    <td>
                        <span class="status-badge ${day.status.toLowerCase()}">
                            ${day.status}
                        </span>
                    </td>
                    <td>${reason}</td>
                </tr>
            `;
        })
        .join("");

    container.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>${t.date}</th>
                        <th>${t.cost}</th>
                        <th>${t.status}</th>
                        <th>${t.reason}</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

function renderDashboard(data) {
    document.getElementById("kpi-total").textContent =
        `$${Number(data.grand_total).toFixed(2)}`;
    document.getElementById("kpi-threshold").textContent =
        `$${Number(data.threshold).toFixed(2)}`;
    document.getElementById("kpi-days").textContent = data.days_count;

    const anomalies = data.daily_costs.filter(
        (day) => day.status !== "NORMAL",
    ).length;

    document.getElementById("kpi-anomalies").textContent = anomalies;

    applyStaticText();
    renderCharts(data);
    renderAlertHistory(data);
}

async function loadDashboard(idToken) {
    try {
        const response = await fetch(API_ENDPOINT, {
            headers: {
                Authorization: `Bearer ${idToken}`,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        latestData = await response.json();

        document.getElementById("status").style.display = "none";
        document.getElementById("content").style.display = "block";

        renderDashboard(latestData);
    } catch (error) {
        document.getElementById("status").textContent =
            `❌ ${translations[currentLang].error}${error.message}`;
    }
}

const langToggle = document.getElementById("lang-toggle");

langToggle.addEventListener("click", () => {
    currentLang = currentLang === "vi" ? "en" : "vi";
    langToggle.textContent = currentLang === "vi" ? "EN" : "🇻🇳 VI";

    if (latestData) {
        renderDashboard(latestData);
    } else {
        applyStaticText();
    }
});

const themeToggle = document.getElementById("theme-toggle");

themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");

    themeToggle.textContent = document.body.classList.contains("dark-mode")
        ? "☀️"
        : "🌙";

    Chart.defaults.color = document.body.classList.contains("dark-mode")
        ? "#ffffff"
        : "#666";

    Object.values(charts).forEach((chart) => chart && chart.update());
});

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
    } catch (error) {
        sessionStorage.removeItem("id_token");
        showAuthenticationState(false);

        document.getElementById("status").textContent =
            `Authentication error: ${error.message}`;
    }
}

loginButton.addEventListener("click", signIn);
logoutButton.addEventListener("click", signOut);

initializeDashboard();
```

Đến đây, chúng ta đã hoàn tất việc thiết lập cơ chế xác thực bảo mật với **Amazon Cognito** cho Web Dashboard. Chúng ta cần triển khai lại bằng dòng lệnh:

```bash
terraform apply
```

### Nội dung tiếp theo

- [Kiểm thử hệ thống](5-Workshop/5.7-Testing)