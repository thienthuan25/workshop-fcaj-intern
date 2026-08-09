---
title : "Kiểm thử hệ thống"
date : 2024-01-01
weight : 7
chapter : false
pre : " <b> 5.7 </b> "
---

### Tổng Quan

Sau khi đã triển khai đầy đủ các thành phần, trong phần này chúng ta sẽ kiểm thử toàn bộ hệ thống **CloudCost Insight** từ đầu đến cuối. Mục tiêu là xác minh các luồng hoạt động đúng và phối hợp chặt chẽ với nhau.

Chúng ta sẽ kiểm thử theo 4 nhóm chính:

- Luồng thu thập và phân tích dữ liệu chi phí.
- Cơ chế phát hiện bất thường và cảnh báo qua Email theo 3 mức.
- Cơ chế xử lý lỗi bằng **Dead Letter Queue**.
- Cơ chế giám sát bằng **CloudWatch Alarm** và **Web Dashboard**.

{{% notice note %}}
Nếu tài khoản AWS của bạn là tài khoản mới hoặc bạn mới chạy hệ thống, chưa qua 24 giờ để **Cost Explorer** ghi nhận dữ liệu chi phí thì chúng ta sẽ tiếp tục sử dụng dữ liệu mô phỏng để kiểm thử đầy đủ các trường hợp phát hiện bất thường. Khi triển khai với tài khoản có chi phí thực tế, hệ thống hoạt động tương tự với dữ liệu thật từ **Cost Explorer**.
{{% /notice %}}

### 1. Kiểm Thử Luồng Thu Thập Dữ Liệu

Trước tiên, chúng ta kiểm tra **Lambda Collector** có thu thập dữ liệu và ghi vào S3 đúng hay không. Trên **AWS Console**, mở hàm Lambda Collector và chạy thử với một sự kiện rỗng.

**1.** Kiểm tra **Lambda Collector**:

- Truy cập vào **Lambda**, chọn **cloudcost-insight-collector**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_1.png)

- Chọn mục **Test** và chạy một sự kiện rỗng.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_2.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_3.png)

- Kết quả kì vọng: 

    + Trả về **statusCode: 200**.
    + Log ghi nhận việc gọi **Cost Explorer**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_4.png)

**2.** Kiểm tra dữ liệu đã được ghi vào S3 theo đúng cấu trúc phân vùng theo năm/tháng/ngày:

- Truy cập vào **S3** và chọn bucket của bạn.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_5.png)

- Kết quả kì vọng: Có các thư mục chứa file JSON chứa dữ liệu chi phí.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_6.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_7.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_8.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_9.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/testing_10.png)

### 2. Kiểm Thử Phát Hiện Chi Phí Bất Thường

Chúng ta sẽ kiểm thử cho 3 mức cảnh báo: **INFO**, **WARNING**, **CRITICAL**. Để kiểm thử ba mức cảnh báo, chúng ta chuẩn bị dữ liệu chi phí đã mô phỏng trong S3 cho từng trường hợp xảy ra. Logic phân loại dựa trên 2 tiêu chí:

- Ngưỡng ngân sách.
- Mức tăng đột biến so với trung bình lịch sử.

| Mức cảnh báo | Dữ liệu | Kết quả mong đợi |
| --- | --- | --- |
| INFO | Chi phí thấp, không vượt ngưỡng | Không gửi email cảnh báo |
| WARNING | Chi phí vượt ngưỡng nhưng chưa đột biến | Gửi email cảnh báo ở mức WARNING |
| CRITICAL | Chi phí tăng đột biến so với trung bình | Gửi email cảnh báo ở mức CRITICAL |

Với mỗi mức cảnh báo, chúng ta gửi sự kiện tương ứng vào SQS, sau đó theo dõi kết quả phân loại dựa trên CloudWatch Logs của Analyzer.

**1.** INFO:

- **Analyzer** tự động kích hoạt sau khi kích hoạt **Collector**.

- Truy cập **Lambda**, chọn **cloudcost-insight-analyzer**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/info_1.png)

- Chọn Tab **Monitoring**, sau đó chọn **View CloudWatch Logs**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/info_2.png)

- Chọn vào Log mới nhất.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/info_3.png)

- Kết quả mong đợi: log phân loại đúng mức **NORMAL**, không cần gửi email cảnh báo.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/info_4.png)

**2.** WARNING:

- Truy vập vào **Lambda**, chọn **cloudcost-insight-analyzer**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/info_1.png)

- Chọn Tab **Test** và test với dữ liệu **JSON** ở múc **WARNING** đã được chạy script sinh dữ liệu mô phỏng chi phí.

```json
{
  "Records": [
    {
      "body": "{\"date\": \"2026-06-25\", \"s3_key\": \"cost-data/year=2026/month=06/day=25/cost_2026-06-25.json\", \"total_cost\": 12.0}"
    }
  ]
}
```

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/warning_1.png)

- Kết quả mong đợi: Log ghi nhận mức cảnh báo **WARNING** và email cảnh báo.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/warning_2.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/warning_3.png)

**3.** CRITICAL:

- Ở cửa sổ Console của **cloudcost-insight-analyzer**, tiếp tục test với dữ **JSON** ở mức **CRITICAL** đã được chạy script sinh dữ liệu mô phỏng chi phí.

```json
{
  "Records": [
    {
      "body": "{\"date\": \"2026-07-05\", \"s3_key\": \"cost-data/year=2026/month=07/day=05/cost_2026-07-05.json\", \"total_cost\": 52.0}"
    }
  ]
}
```

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/critical_1.png)

- Kết quả mong đợi: Log ghi nhận mức cảnh báo **CRITICAL** và email cảnh báo.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/critical_2.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/critical_3.png)

### 3. Kiểm Thử Cơ Chế Xử Lý Lỗi

#### 3.1. Dead Letter Queue

Tiếp theo, chúng ta kiểm thử khả năng chịu lỗi của hệ thống.

**1.** Trên Terminal, gửi một sự kiện lỗi trỏ tới một file không tồn tại trong S3 vào hàng đợi chính:

```bash
aws sqs send-message --queue-url $(terraform output -raw sqs_events_queue_url) --message-body '{"date": "2099-01-01", "s3_key": "cost-data/unknown.json", "total_cost": 0}'
```

- Kết quả mong đợi: Message được nhận.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_1.png)

**2.** Analyzer retry rồi thất bại:

- Truy cập vào **CloudWatch**, chọn Tab **Log management**, chọn tiếp **/aws/lambda/cloudcost-insight-analyzer**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_2.png)

- Chọn vào **Log stream** mới nhất.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_3.png)

- Kết quả mong đợi: Log lỗi **NoSuchKey** và lặp lại nhiều lần.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_4.png)

- Tiếp theo, truy cập vào **SQS**, chọn **cloudcost-insight-dlq**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_5.png)

- Chọn **Send and receive message**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_6.png)

- Kéo xuống chọn **Poll for messages**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_7.png)

- Kết quả mong đợi: Message được gửi vào **Dead Letter Queue**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_8.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dlq_9.png)

#### 3.2. SQS Partial Batch Failure

Trong thực tế, một lần Lambda Analyzer được kích hoạt có thể nhận nhiều message từ hàng đợi SQS. Nếu chỉ một message bị lỗi, việc để toàn bộ batch thất bại sẽ làm các message đã xử lý thành công bị xử lý lại, dẫn đến xử lý trùng lặp và gây lãng phí tài nguyên.

Cơ chế SQS partial batch failure cho phép Lambda trả về chính xác những message xử lý thất bại. SQS chỉ retry các message này, trong khi các message hợp lệ còn lại được xác nhận là đã xử lý thành công và không bị chạy lại.

Trong phần này, chúng ta sẽ gửi một batch gồm message hợp lệ và message lỗi để xác minh Analyzer xử lý đúng từng message, chỉ đưa message lỗi vào cơ chế retry hoặc Dead Letter Queue.

**1.** Trên cửa số AWS:

- Truy cập vào Lambda.
- Truy cập vào **cloudcost-insight-analyzer**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_1.png)

- Mở tab Configuration -> Trigger.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_2.png)

- Mở SQS Trigger và xác nhận có bật Report batch item failures.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_3.png)

- Tính năng này giúp hệ thống hoạt động chính xác theo cơ chế **Partial Batch Failure**, giúp tiết kiệm tài nguyên, ngăn chặn tình trạng xử lý trùng lặp và đảm bảo chỉ những dữ liệu thật sự bị lỗi mới bị đưa vào **Dead Letter Queue**.

**2.** Trên cửa sổ Lambda **cloudcost-insight-analyzer**:

- Truy cập Tab **Test**.
- Tạo event có 1 record đúng và 1 record lỗi:

```json
{
  "Records": [
    {
      "messageId": "good-message",
      "body": "{\"date\":\"2026-07-03\",\"s3_key\":\"cost-data/year=2026/month=07/day=03/cost_2026-07-03.json\"}"
    },
    {
      "messageId": "bad-message",
      "body": "{invalid-json}"
    }
  ]
}
```

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_4.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_5.png)

- Bấm chọn **Test**.
- Kết quả mong đợi: Message lỗi được đưa vào DLQ và message đúng được xử lý thành công.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_6.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_7.png)

#### 3.3. Kiểm Thử Xử Lý Lỗi Khi Analyzer Không Đọc Được Dữ Liệu Từ S3

Analyzer cần đọc file dữ liệu chi phí từ Amazon S3 để phân tích và xác định mức cảnh báo. Nếu file không tồn tại, đường dẫn s3_key sai hoặc xảy ra lỗi truy cập S3, Lambda không được bỏ qua lỗi và coi message là đã xử lý thành công.

Trong phần này, chúng ta sẽ kiểm tra việc Analyzer ghi nhận lỗi đầy đủ trên CloudWatch Logs và trả về trạng thái thất bại cho SQS. Khi đó, SQS sẽ tự động retry message theo cấu hình; nếu message tiếp tục thất bại sau số lần retry cho phép, nó sẽ được chuyển vào Dead Letter Queue để kiểm tra và xử lý sau.

#### 3.3.1. Kiểm thử không có file lịch sử

File lịch sử chỉ được dùng để tính mức chi phí trung bình nhằm phát hiện chi phí tăng đột biến, không phải dữ liệu bắt buộc để xử lý chi phí của ngày hiện tại. Ví dụ, với ngày 18-06-2026 có chi phí là $9.00, Analyzer cần:

- File chính: `2026-06-18.json`: Đây là dữ liệu bắt buộc. Nếu file này không tồn tại, Analyzer không biết chi phí ngày cần phân tích là bao nhiêu → record thất bại và phải retry.
- Các file lịch sử từ ngày 17-06-2026 trở về trước: Đây là dữ liệu bổ sung để tính trung bình 14 ngày. Nếu thiếu, Analyzer vẫn biết chi phí ngày 18-06-2026 là $9.00, vẫn so sánh được với ngưỡng ngân sách $10.00, nên vẫn có thể kết luận NORMAL.

Điều này giúp hệ thống vẫn hoạt động vào những ngày đầu tiên sau khi triển khai, khi chưa có đủ 14 ngày dữ liệu lịch sử. Khi dữ liệu tích lũy dần, Analyzer sẽ bắt đầu tính trung bình và kích hoạt quy tắc phát hiện chi phí tăng đột biến.

**1.** Trên cửa sổ AWS, truy cập S3, chọn Cost Data Bucket của bạn.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_11.png)

**2.** Copy một S3 key `.json` đang tồn tại, ví dụ:

```
cost-data/year=2026/month=07/day=03/cost_2026-07-03.json
```

- Vào **Lambda**, chọn **cloudcost-insight-analyzer**, mở Tab **Test** và tạo event như sau:

```json
{
  "Records": [
    {
      "messageId": "test-s3-not-found-001",
      "body": "{\"date\":\"2099-01-01\",\"s3_key\":\"cost-data/not-found.json\",\"total_cost\":0}"
    }
  ]
}
```

**3.** Kết quả mong đợi:

- Trả về response sau:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_12.png)

- Message có **itemIdentifier** là **test-s3-not-found-001** không thể được xử lý do Analyzer không đọc được file dữ liệu tương ứng từ Amazon S3. Lambda trả message ID này trong mảng **batchItemFailures** để thông báo cho Amazon SQS rằng chỉ message này cần được giữ lại để retry.
- Chúng ta có thể xem Log của nó:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_13.png)

#### 3.3.2. Kiểm thử file lịch sử không hợp lệ

**1.** Tạo file `cost_2099-01-01.json` có nội dung cố ý sai:

```json
{invalid-json}
```

**2.** Vào **Cost Data bucket** và tạo thư mục chứa file JSON này với cấu trúc thư mục như sau:

`cost-data/year=2099/month=01/day=01/`

Upload file `cost_2099-01-01.json` vào thư mục này:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_1.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_2.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_3.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_4.png)

**3.** Tạo event trên Lambda:

- Truy cập vào Lambda, chọn **cloudcost-insight-analyzer**.
- Mở Tab **Test** và tạo event như sau:

```json
{
  "Records": [
    {
      "messageId": "corrupt-history-test",
      "body": "{\"date\":\"2099-01-02\",\"s3_key\":\"cost-data/year=2026/month=07/day=03/cost_2026-07-03.json\"}"
    }
  ]
}
```

- Bấm chọn **Test**.
- Kết quả mong đợi: Trả về response sau;

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_5.png)

- Message có **itemIdentifier** là **corrupt-history-test** không thể được xử lý do nội dung file `2099-01-01.json` sai cú pháp JSON. Lambda trả message ID này trong mảng **batchItemFailures** để thông báo cho Amazon SQS rằng chỉ message này cần được giữ lại để retry.
- Chúng ta có thể xem Log của nó:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/invalid_6.png)

### 4. Kiểm thử giám sát bằng CloudWatch Alarm

Khi sự kiện lỗi ở bước 3 khiến **Analyzer** phát sinh lỗi và có message rơi vào **DLQ**, các **CloudWatch Alarm** tương ứng sẽ chuyển sang trạng thái **ALARM** và gửi email cảnh báo sự cố.

- Truy cập vào **CloudWatch**, chọn mục **Alarm**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/partial_10.png)

- Kết quả mong đợi: **cloudcost-insight-analyzer-errors** và **cloudcost-insight-dlq-has-messages** trong trạng thái **In alarm**.

- Email thông báo.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/alarm_1.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/alarm_2.png)

- Sau một khoảng thời gian, chúng ta sẽ có email chuyển trạng thái của **cloudcost-insight-analyzer-errors** từ **ALARM** sang **OK** vì **Analyzer** không còn lỗi mới nữa, **CloudWatch** không nhận được datapoint lỗi nào. Dó đó Alarm tự chuyển về **OK**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/alarm_3.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/alarm_4.png)

### 5. Bảo Mật Dashboard

Dashboard CloudCost Insight hiển thị dữ liệu chi phí AWS, vì vậy dữ liệu chỉ được cung cấp cho người dùng đã được xác thực. Trong phần này, chúng ta sẽ kiểm thử cơ chế xác thực bằng Amazon Cognito và kiểm tra API Gateway chỉ chấp nhận các request có JWT hợp lệ.

Bên cạnh đó, chúng ta cũng xác minh cấu hình CORS chỉ cho phép Dashboard được triển khai trên CloudFront gọi API. Việc kết hợp Cognito và CORS giúp hạn chế truy cập trái phép, bảo vệ dữ liệu chi phí và đảm bảo chỉ người dùng đã đăng nhập mới có thể sử dụng Dashboard.

CORS chỉ giới hạn nơi trình duyệt được phép gọi API. Nó không ngăn ai đó gọi API bằng curl/Postman. Vì vậy, chúng ta sẽ tiến hành kiểm tra cả 2 cơ chế bảo mật này:

- CORS.
- JWT authentication Cognito.

**1.** Lấy các giá trị cần thiết:

```bash
export API_ENDPOINT=$(terraform output -raw api_endpoint)
export WEB_ORIGIN=$(terraform output -raw web_dashboard_url)
export USER_POOL_ID=$(terraform output -raw user_pool_id)
export USER_POOL_CLIENT_ID=$(terraform output -raw user_pool_client_id)
export AWS_REGION="us-east-1"
```
**2.** Tạo một tài khoản test trong Cognito Console:

- Truy cập vào **Cognito**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_1.png)

- Chọn vào **User Pool** của project.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_2.png)

- Trong Tab **User**, chọn **Create User**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_3.png)

- Điền email, password. Sau đó bấm **Create User**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_4.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_5.png)

**3.** Kiểm thử gọi API không có Token:

- Khi tạo user, **Cognito** mặc định đặt trạng thái **FORCE_CHANGE_PASSWORD**, nghĩa là lần đăng nhập đầu tiên sẽ yêu cầu đổi mật khẩu. Đề dùng mật khẩu cố định cho kiểm thử, chúng ta cần **set permanent password** qua AWS CLI:

```bash
aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username YOUR_EMAIL \
  --password "YOUR_FIXED_PASSWORD" \
  --permanent
```

- Kiểm thử gọi API không có Token bằng cách dùng curl:

```bash
curl -i "$API_ENDPOINT"
```
- Kết quả mong đợi:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_6.png)

- Mã trạng thái 401 Unauthorized cho biết request chưa được xác thực nên không được phép truy cập API. Do lệnh curl không gửi header Authorization: Bearer <JWT>, API Gateway không chuyển request đến Lambda xử lý dữ liệu chi phí.
- Header www-authenticate: Bearer cho biết API yêu cầu client cung cấp Bearer Token, cụ thể là JWT được Amazon Cognito cấp sau khi người dùng đăng nhập thành công. Kết quả này xác nhận JWT Authorizer đã được cấu hình và hoạt động đúng, giúp ngăn các truy cập không xác thực vào dữ liệu chi phí trên Dashboard.

**4.** Kiểm thử gọi API bằng JWT Cognito hợp lệ:

- Lấy ID token của user:

```bash
export ID_TOKEN=$(aws cognito-idp initiate-auth \
  --region "$AWS_REGION" \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$USER_POOL_CLIENT_ID" \
  --auth-parameters USERNAME="YOUR_EMAIL",PASSWORD="YOUR_PASSWORD" \
  --query 'AuthenticationResult.IdToken' \
  --output text)
```

- Kiểm thử:

```bash
curl -i "$API_ENDPOINT" -H "Authorization: Bearer $ID_TOKEN" -H "Origin: $WEB_ORIGIN"
```

- Kết quả mong đợi:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_7.png)

Mã trạng thái **200 OK** xác nhận **API Gateway** đã kiểm tra thành công token trong header authorization và cho phép request đi tiếp đến **Lambda API**. Hàm Lambda sau đó tiến hành đọc dữ liệu chi phí từ **Amazon S3**, tổng hợp thông tin và trả về phản hồi JSON cho Dashboard. Bên cạnh đó, header **access-control-allow-origin** cũng xác nhận cơ chế **CORS** đang hoạt động chính xác, chỉ cho phép Dashboard triển khai trên domain **CloudFront** của dự án truy cập API. API tuyệt đối không sử dụng cấu hình mở để ngăn chặn các website lạ gọi API trực tiếp từ trình duyệt. Dữ liệu JSON trả về bao gồm danh sách chi phí theo ngày, trạng thái bất thường và các dịch vụ tốn kém nhất. Điều này minh chứng toàn bộ luồng bảo mật và truy xuất dữ liệu hoạt động hoàn hảo từ bước người dùng đăng nhập **Cognito**, nhận **JWT**, gửi token đến **API Gateway** để xác thực, và cuối cùng được **Lambda** trả về dữ liệu chi phí.

**5.** Kiểm thử CORS từ CloudFront domain hợp lệ

- Mô phỏng **preflight request** từ dashboard:

```bash
curl -i -X OPTIONS "$API_ENDPOINT" \
  -H "Origin: $WEB_ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization,content-type"
```

- Kết quả mong đợi:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_8.png)

Kết quả kiểm thử cho thấy **API Gateway** đã xử lý thành công **preflight request** từ Dashboard trên **CloudFront**. Mã trạng thái **204 No Content** là phản hồi chính xác do request **OPTIONS** chỉ được trình duyệt gửi đi nhằm kiểm tra chính sách **CORS** nên API không cần trả về nội dung. Header **access-control-allow-origin** xác nhận chỉ domain hợp lệ của Dashboard mới được phép gọi API. Header **access-control-allow-methods** giới hạn ở hai phương thức **GET** và **OPTIONS** để đảm bảo an toàn cho chức năng đọc dữ liệu. Ngoài ra, header **access-control-allow-headers** cho phép frontend gửi header authorization nhằm đính kèm token **Cognito** khi gọi API chính thức. Trình duyệt không lưu cache kết quả preflight này do header **access-control-max-age** được đặt bằng 0. Qua đó, trình duyệt đã nhận đủ quyền để tiếp tục gửi request dữ liệu kèm JWT đến hệ thống.

**6.** Kiểm thử CORS từ domain không hợp phép

- Thực hiện:

```bash
curl -i -X OPTIONS "$API_ENDPOINT" \
  -H "Origin: https://evil.example" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization"
```

- Kết quả mong đợi:

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/cognito_9.png)

Khi kiểm thử từ một domain không hợp lệ, hệ thống trả về mã **204 No Content** nhưng hoàn toàn vắng mặt header **Access-Control-Allow-Origin**. Điều này minh chứng **API Gateway** không cấp quyền **CORS** cho các domain lạ ngoài dự án. Việc thiếu các header cho phép sẽ khiến trình duyệt web tự động chặn website gian lận thực hiện request lấy dữ liệu. Cấu hình bảo mật này đảm bảo chỉ duy nhất frontend triển khai trên **CloudFront** mới có thể gọi API thành công từ môi trường trình duyệt.

Tóm lại, các kịch bản kiểm thử bảo mật cho Dashboard đã hoàn tất thành công. **API Gateway** hoạt động chặt chẽ khi từ chối các request vô danh bằng mã **401 Unauthorized** và chỉ cung cấp dữ liệu với mã **200 OK** khi nhận được token hợp lệ từ **Amazon Cognito**. Cơ chế **CORS** cũng phát huy tác dụng khi cấp đủ quyền cho domain **CloudFront** chính chủ thông qua **preflight request**, đồng thời chặn đứng truy cập từ các domain lạ. Sự kết hợp giữa **JWT Authorizer** và **CORS** tạo nên một lớp bảo vệ vững chắc, đảm bảo chỉ người dùng đã xác thực mới có quyền truy cập vào dữ liệu chi phí AWS của hệ thống.

### 6. Web Dashboard

Tiếp theo, chúng ta sẽ tiến hành truy cập vào đường link URL CloudFront của dashboard. 

Trên terminal, thực hiện:

```bash
terraform output web_dashboard_url
```

Kết quả trả về là URL CloudFront của dashboard.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dashboard_0.png)

Truy cập vào đường link, tiến hành đăng nhập.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dashboard_3.png)

Nhập email và mật khẩu đã đăng kí trên **Cognito**.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dashboard_4.png)

Sau khi đăng nhập thành công, chúng ta đã có thể truy cập vào giao diện và theo dõi các chỉ số chi phí.

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dashboard_5.png)

![Testing](/workshop-fcaj-intern/images/5-Workshop/5.7-Testing/dashboard_6.png)

### 7. Tổng Kết Kiểm Thử

Sau khi hoàn thành các bước kiểm thử trên, hệ thống **CloudCost Insight** đã được kiểm chứng hoạt động hoàn chỉnh và tự động end-to-end:

- Thu thập dữ liệu chi phí tự động và lưu trữ đúng cấu trúc.
- Phát hiện bất thường và cảnh báo qua email theo ba mức.
- Xử lý lỗi an toàn bằng **Dead Letter Queue**.
- Tự giám sát sức khỏe hệ thống bằng **CloudWatch Alarm**.
- Trực quan hóa dữ liệu qua **Web Dashboard** có thể truy cập công khai.

### Nội Dung Tiếp Theo

- [CI/CD](5-Workshop/5.8-CI-CD/)