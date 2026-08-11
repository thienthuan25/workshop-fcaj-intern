---
title : "Web Dashboard"
date : 2024-01-01
weight : 6
chapter : false
pre : " <b> 5.6. </b> "
---

### Introduction

In this section, we will build a custom Web Dashboard to visualize cost data. Instead of using an existing Business Intelligence service, we will develop the entire dashboard ourselves to gain full control over both the user interface and the data while keeping operational costs as low as possible.

The Web Dashboard consists of two main components:

- **Backend** includes a Lambda API function that reads cost data from S3 and an API Gateway that exposes an endpoint for the web application.
- **Frontend** is a static website that uses `Chart.js` to render charts. It is hosted on Amazon S3 and distributed through CloudFront.

![Dashboard](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Content

1. [Backend](../5.6-Dashboard/5.6.1-Backend/)
2. [Frontend](../5.6-Dashboard/5.6.2-Frontend/)
3. [Authentication with Cognito](../5.6-Dashboard/5.6.3-Authentication-Cognito/)

