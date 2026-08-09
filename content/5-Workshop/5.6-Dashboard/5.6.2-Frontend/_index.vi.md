---
title : "Frontend"
date : 2024-01-01
weight : 2
chapter : false
pre : " <b> 5.6.2 </b> "
---

### Tạo giao diện

Chúng ta sẽ tạo giao diện Web trong thư mục `terraform/web`.

**1.** File `index.html` chứa cấu trúc trang:

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

**2.** File `style.css` chứa toàn bộ định dạng giao diện:

```css
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
    --shadow-color: rgba(0, 0, 0, 0.08);
    --header-bg: linear-gradient(135deg, #232f3e, #ff9900);
}

body.dark-mode {
    --bg-color: #1a202c;
    --text-color: #ffffff;
    --card-bg: #2d3748;
    --label-color: #a0aec0;
    --heading-color: #ffffff;
    --shadow-color: rgba(0, 0, 0, 0.3);
}

body {
    font-family: 'Segoe UI', Arial, sans-serif;
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
#lang-toggle {
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
#lang-toggle:hover {
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

.kpi-card .value.ok {
    color: #38a169;
}

.chart-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
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

.chart-small {
    max-width: 850px;
    margin: 0 auto;
}

.status {
    text-align: center;
    padding: 40px;
    color: #718096;
}

@media (max-width: 900px) {
    .chart-grid {
        grid-template-columns: 1fr;
    }
}
```

**3.** File `script.js` chứa logic gọi API và vẽ biểu đồ bằng **Chart.js**:

```javascript
const API_ENDPOINT = "REPLACE_MY_API_ENDPOINT";

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
    },
};

// Ngôn ngữ hiện tại
let currentLang = "en";
let latestData = null;
let charts = {};

// Màu theo trạng thái
const statusColor = (s) =>
    s === "CRITICAL" ? "#e53e3e" : s === "WARNING" ? "#dd6b20" : "#38a169";

// Áp dụng ngôn ngữ vào các nhãn tĩnh (không phải biểu đồ)
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
}

// Vẽ lại các biểu đồ theo ngôn ngữ
function renderCharts(data) {
    const t = translations[currentLang];

    Object.values(charts).forEach(c => c && c.destroy());

    const labels = data.daily_costs.map(d => d.date);
    const totals = data.daily_costs.map(d => d.total);
    const colors = data.daily_costs.map(d => statusColor(d.status));
    const threshold = Number(data.threshold);

    // Biểu đồ xu hướng
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

    // Biểu đồ donut
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

    // Biểu đồ top dịch vụ
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

async function loadDashboard() {
    try {
        const res = await fetch(API_ENDPOINT);
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

// Nút chuyển ngôn ngữ
const langToggle = document.getElementById("lang-toggle");
langToggle.addEventListener("click", () => {
    currentLang = currentLang === "vi" ? "en" : "vi";
    langToggle.textContent = currentLang === "vi" ? "VI" : "EN";
    applyStaticText();
    if (latestData) renderCharts(latestData); // vẽ lại biểu đồ với nhãn ngôn ngữ mới
});

// Nút dark mode
const themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    themeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
    Chart.defaults.color = document.body.classList.contains("dark-mode") ? "#ffffff" : "#666";
    Object.values(charts).forEach(c => c && c.update());
});

// Khởi tạo nhãn ngôn ngữ ban đầu
applyStaticText();
loadDashboard();
```

Giao diện gồm nhiều biểu đồ xu hướng chi phí kèm đường ngưỡng và đánh dấu ngày bất thường, biểu đồ tỷ trọng theo dịch vụ, và các chỉ số KPI tổng quan. Ngoài ra còn có chức năng chuyển đổi giao diện sáng tối và chuyển đổi ngôn ngữ Anh Việt.

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_1.png)

### Host Web lên S3 và CloudFront

**1.** Chúng ta sẽ tạo file `terraform/web_hosting.tf` để host giao diện lên **S3** và phân phối qua **CloudFront** với HTTPS. Để bảo mật, bucket Web không được mở public trực tiếp mà chỉ cho phép **CloudFront** đọc thông qua **Origin Access Control**.

```hcl
# Host Website lên S3 + CloudFront

# S3 bucket lưu web tĩnh
resource "aws_s3_bucket" "web" {
  bucket = "${var.project_name}-web-${data.aws_caller_identity.current.account_id}"
}

# static website hosting
resource "aws_s3_bucket_website_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "index.html"
  }
}

# CloudFront + Origin Access Control 
resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "${var.project_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# chặn truy cập public trực tiếp vào bucket
resource "aws_s3_bucket_public_access_block" "web" {
  bucket                  = aws_s3_bucket.web.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  default_root_object = "index.html"
  comment             = "CloudCost Insight Web Dashboard"

  origin {
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_id                = "s3-web"
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-web"
    viewer_protocol_policy = "redirect-to-https" # HTTPS
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    # giúp Dashboard luôn tải phiên bản file mới nhất từ S3 thay vì dùng bản cũ
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  price_class = "PriceClass_100" #cheap
}

# bucket policy: Cloudfront đọc S3
data "aws_iam_policy_document" "web_bucket_policy" {
  statement {
    sid       = "AllowCloudFrontRead"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.web.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id
  policy = data.aws_iam_policy_document.web_bucket_policy.json
}

# upload index.html lên S3
resource "aws_s3_object" "index" {
  bucket        = aws_s3_bucket.web.id
  key           = "index.html"
  source        = "${path.module}/web/index.html"
  content_type  = "text/html"
  cache_control = "no-cache, no-store, must-revalidate"
  etag          = filemd5("${path.module}/web/index.html")
}

# upload style.css lên S3
resource "aws_s3_object" "style" {
  bucket        = aws_s3_bucket.web.id
  key           = "style.css"
  source        = "${path.module}/web/style.css"
  content_type  = "text/css"
  cache_control = "no-cache, no-store, must-revalidate"
  etag          = filemd5("${path.module}/web/style.css")
}

# upload script.js lên S3
locals {
    rendered_script = replace (
        file("${path.module}/web/script.js"),
        "REPLACE_MY_API_ENDPOINT",
        "${trim(aws_apigatewayv2_stage.default.invoke_url, "/")}/costs"
    )
}

resource "aws_s3_object" "script" {
  bucket = aws_s3_bucket.web.id
  key    = "script.js"

  content       = local.rendered_script
  content_type  = "application/javascript"
  cache_control = "no-cache, no-store, must-revalidate"
  etag          = md5(local.rendered_script)
}
```

Việc dùng **Origin Access Control** là một điểm bảo mật quan trọng. Bucket Web hoàn toàn không mở công khai, mọi truy cập phải đi qua CloudFront với HTTPS, tránh lộ dữ liệu ra Internet.

**2.** Mở file `terraform/outputs.tf` và thêm đoạn cấu hình sau vào cuối file.

```hcl
# Web Dashboard
output "web_dashboard_url" {
  description = "URL to access Web Dashboard (HTTPS via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.web.domain_name}"
}

output "web_bucket_name" {
  description = "S3 bucket name for static web"
  value       = aws_s3_bucket.web.id
}
```

### Triển khai và truy cập Dashboard

**1.** Trên Terminal, triển khai phần Frontend:

```bash
terraform apply
```

**2.** Lấy đường link URL của Dashboard:

```bash
terraform output web_dashboard_url
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_2.png)

**3.** Truy cập vào đường link hiện ra trên Terminal, ta sẽ vào giao diện của Website: 

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_3.png)

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_4.png)

Giao diện thể hiện được **tổng chi phí**, **ngưỡng cảnh báo**, **số ngày theo dõi**, **số ngày bất thường**, và 3 biểu đồ trực quan.

**Biểu đồ 1: Xu hướng chi phí theo ngày (Trend Chart):**

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_5.png)

- Trục X (ngang): thể hiện các ngày theo dõi.
- Trục Y (dọc): thể hiện chi phí ($) mỗi ngày.
- Đường ngang màu xanh: thể hiện chi phí thực tế biến động theo ngày.
- Nét đứt màu đỏ: đây là đường ngang cố định, thể hiện ngưỡng ngân sách. Nếu chi phí vượt lên trên đường này thì vượt ngưỡng.
- Vùng nền màu xanh: được tô dưới đường màu xanh thể hiện xu hướng.

**Biểu đồ 2: Tỷ trọng theo dịch vụ (Service Chart):**

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_6.png)

- Mỗi phần của hình tròn là chi phí của mỗi dịch vụ. Phần càng lớn chứng tỏ chi phí của dịch vụ đó càng cao.
- Trên mỗi phần có tên các dịch vụ nếu chúng ta chọn vào.
- Mỗi dịch vụ là một màu riêng biệt.
- Danh sách dịch vụ + màu tương ứng ở phía dưới biểu đồ.

**Biểu đồ 3: Top dịch vụ (Bar Chart):**

![Dashboard](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.2-Frontend/frontend_7.png)

- Biểu đồ thể hiện top 5 các dịch vụ có chi phí cao nhất.
- Trục X (ngang): thể hiện chi phí của dịch vụ.
- Trục Y (dọc): thể hiện tên dịch vụ tương ứng.

### Nội dung tiếp theo

- [Xác thực với Amazon Cognito](../5.6.3-Authentication-Cognito/)