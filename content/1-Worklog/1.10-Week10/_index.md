---
title: "Week 10 Worklog"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.10. </b> "
---

### Week 10 Objectives:

* Build the web frontend for the dashboard (`index.html`, `style.css`, `script.js`), using Chart.js to visualize cost data.
* Host the frontend on AWS using S3 Web Hosting and CloudFront with HTTPS.
* Add Dashboard authentication using Amazon Cognito and a JWT Authorizer for API Gateway.
* Perform end-to-end testing of the entire Dashboard flow, from Cognito login to the API and cost data.
* Refine and upgrade the Dashboard: tweak charts, add a light/dark mode, and implement bilingual EN/VI toggle.
* Maintain team coordination: discuss plans before starting and summarize results at the end of each day.

### Tasks Implemented During the Week:

| Day | Task | Start Date | End Date | References |
| --- | --- | --- | --- | --- |
| 2 | - Write web frontend (UI and logic): <br>&emsp; + Discuss the daily work plan with the team before starting. <br>&emsp; + Write `index.html` (page structure) and `style.css` (UI). <br>&emsp; + Write `script.js` to call the API endpoint, process JSON, and draw charts using Chart.js. <br>&emsp; + Draw charts: cost trends (threshold line + anomaly markers), top services, alert history, KPIs. <br>&emsp; + At the end of the day, summarize and share results with the team. | 13/07/2026 | 13/07/2026 | - Chart.js Documentation: <br> https://www.chartjs.org/docs/latest/ <br> - MDN Fetch API: <br> https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API |
| 3 | - Host frontend on AWS (S3 + CloudFront): <br>&emsp; + Discuss the daily work plan with the team before starting. <br>&emsp; + Create an S3 bucket (Web Hosting) and upload 3 UI files using Terraform. <br>&emsp; + Configure CloudFront (HTTPS) and Origin Access Control for security, blocking direct public access to S3. <br>&emsp; + Get the CloudFront link to access the Dashboard. <br>&emsp; + At the end of the day, summarize and share results with the team. | 14/07/2026 | 14/07/2026 | - Amazon CloudFront + S3: <br> https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html <br> - Terraform aws_cloudfront_distribution: <br> https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_distribution |
| 4 | - Add Dashboard authentication with Amazon Cognito: <br>&emsp; + Discuss the daily work plan with the team before starting. <br>&emsp; + Create a Cognito User Pool, App Client, and Cognito Domain using Terraform. <br>&emsp; + Configure the API Gateway JWT Authorizer to only accept requests with valid JWTs. <br>&emsp; + Update CORS, only allowing the Dashboard's CloudFront domain to call the API from the browser. <br>&emsp; + Integrate the Authorization Code Flow with PKCE login flow into `script.js`; add login and logout buttons. <br>&emsp; + At the end of the day, summarize and share results with the team. | 15/07/2026 | 15/07/2026 | - Amazon Cognito Developer Guide: <br> https://docs.aws.amazon.com/cognito/ <br> - API Gateway JWT Authorizer: <br> https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html |
| 5 | - End-to-end testing and Dashboard refinement: <br>&emsp; + Discuss the daily work plan with the team before starting. <br>&emsp; + Access the Dashboard via the CloudFront link in the browser and log in using Cognito. <br>&emsp; + Verify the flow: browser to CloudFront/S3, Cognito authenticates and issues a JWT, Dashboard calls API Gateway, Lambda API reads data from S3. <br>&emsp; + Check that charts correctly display cost data and anomaly statuses. <br>&emsp; + Adjust the size of the donut chart for balance, add tooltips displaying amounts with the `$` symbol. <br>&emsp; + Add a light/dark mode UI toggle using CSS variables. <br>&emsp; + At the end of the day, summarize and share results with the team. | 16/07/2026 | 16/07/2026 |  |
| 6 | - Add bilingual toggle (EN/VI) and finalize testing: <br>&emsp; + Discuss the daily work plan with the team before starting. <br>&emsp; + Build a bilingual English/Vietnamese dictionary for labels, titles, authentication messages, and charts. <br>&emsp; + Add a language switch button, update the UI, and redraw charts according to the selected language. <br>&emsp; + Retest the entire Dashboard in both languages, including login, data loading, charts, and light/dark mode. <br>&emsp; + At the end of the day, summarize and share results with the team. | 17/07/2026 | 17/07/2026 |  |

### Week 10 Achievements:

* **Completed web frontend for the Dashboard:** Built the Dashboard UI organized into 3 separate files (`index.html`, `style.css`, `script.js`) following the separation of concerns principle. The Dashboard uses the Chart.js library to visualize cost data with charts for daily cost trends, threshold lines, anomaly markers, service proportion, top costly services, and KPI metrics.
* **Successfully hosted frontend on AWS:** Deployed the Web Dashboard to S3 combined with CloudFront and provided an HTTPS link for users to access. Origin Access Control was applied so that only CloudFront has permission to read content from S3, preventing direct public access to the web bucket.
* **Added authentication with Amazon Cognito:** Deployed a Cognito User Pool, App Client, and Cognito Domain to manage users. The Dashboard uses the Authorization Code Flow with PKCE for users to log in and receive a JWT. API Gateway is configured with a JWT Authorizer, allowing only requests with valid tokens to access cost data. CORS is also restricted so that only the project's CloudFront domain can call the API from the browser.
* **End-to-end testing of the Web Dashboard:** Successfully verified the entire operational flow: the user accesses the Dashboard via CloudFront, logs in with Cognito, receives a JWT, and then the Dashboard calls API Gateway to the Lambda API and S3 to retrieve cost data. The charts correctly display the data and anomaly statuses.
* **UI refinement and light/dark mode addition:** Adjusted the size of the donut chart for balance and added tooltips displaying amounts with the `$` symbol. Added a light/dark UI toggle using CSS variables, helping users choose a suitable interface and improving the user experience.
* **Added bilingual functionality (EN/VI):** Built an English/Vietnamese bilingual toggle mechanism for labels, titles, authentication messages, and chart labels. The Dashboard was retested in both languages, ensuring consistent UI and data display.
* **Team coordination:** Maintained effective teamwork habits throughout the week. Before starting work each day, I discussed the plan with team members, and at the end of each day, summarized the completed tasks so the whole team stayed updated on the progress.