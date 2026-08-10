---
title: "Event 2"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 4.2. </b> "
---

# Bài Thu Hoạch "FCAJ Community Day"

- Thời gian: 09:00 - 12:00 ngày 23/05/2026.
- Địa điểm: Tầng 26, tòa nhà Bitexco, số 02 đường Hải Triều, Phường Sài Gòn, Thành phố Hồ Chí Minh, Việt Nam.

### Mục Đích Của Sự Kiện

Sự kiện **FCAJ Community Day** được tổ chức không chỉ với mục đích chia sẻ kiến thức chuyên sâu về công nghệ, **Cloud (AWS)** và **AI**, mà còn t ạo ra một không gian để cộng đồng công nghệ kết nối, giao lưu và truyền cảm hứng học hỏi lẫn nhau.

### Vai Trò Tham Gia

Trong sự kiện lần này, em tham gia với vai trò là một người tham dự, lắng nghe và tiếp thu các kiến thức thực chiến từ những chuyên gia hàng đầu trong ngành, từ đó nắm bắt các xu hướng công nghệ mới nhất.

### Danh Sách Diễn Giả

Sự kiện FCAJ Community Day lần này với sự tham gia của nhiều chuyên gia và kỹ sư hàng đầu trong lĩnh vực **Điện toán đám mây (Cloud)**, **DevOps** và **AI**. Mở đầu với phần chia sẻ rất hay từ anh **Nguyễn Gia Hưng** (Head of Solutions Architect - Việt Nam & Cambodia). Sau đó đến phần chính với các diễn giả:
- **Tinh Truong** - Platform Engineer tại GoTymeX.
- **Anh Pham** - Cloud Consultant tại G-AsiaPacific Vietnam.
- **Thinh Nguyen** - DevOps Engineer tại STYL Solutions Pte. Ltd.
- **Nhóm Team VIB** - Quán quân cuộc thi **LotusHacks**.
- **Duc Dao** - Solution Architect tại Cloud Kinetics.
- **Vy Lam** - Senior Business Systems Analyst tại VPBank.

### Nội Dung

Sự kiện được chia ra thành nhiều phiên chia sẻ với các chủ đề khác nhau, tập trung vào các công nghệ hiện đại trên nền tảng AWS.

#### Góc Nhìn Về Thị Trường Làm Việc

AI đang làm cho việc tạo ra phần mềm rẻ hơn, dẫn đến nhu cầu về phần mềm và việc làm liên quan sẽ tăng khủng khiếp. Để cạnh tranh, kỹ sư cần trang bị kiến thức nghiệp vụ chuyên ngành và phải có sản phẩm thực tế chứng minh năng lực thay vì chỉ làm demo.

#### Chủ Đề 1: Context Is Everything: Making AI Actually Work for You - Tinh Truong

Phần này nói về tầm quan trọng của ngữ cảnh trong AI. Đa phần, AI trả lời kém không phải do model tệ, mà do ngữ cảnh cung cấp không đủ chi tiết. Không nên mắc lỗi **Internet Puller** (nhồi nhét nhiều tài liệu không liên quan vào trong AI). 

Một prompt tốt cần tuân thủ cấu trúc:

**Mục tiêu - Dữ liệu liên quan - Ràng buộc - Tiêu chí thành công**

#### Chủ Đề 2: Friendly AI Assistant with Amazon Quick - Anh Pham

Chủ đề này tập trung vào việc tận dụng AI để tối ưu hóa hiệu suất làm việc cho doanh nghiệp, cụ thể thông qua các trợ lý AI tự động.

Các nội dung chính gồm:
- Giải quyết bài toán thời gian: Tác giả nhấn mạnh việc quản lý, thường thì chúng ta sẽ mất rất nhiều thời gian để tập hợp dữ liệu và làm báo cáo thủ công. **Amazon Quick** được giới thiệu như một giải pháp thông minh giúp giảm tải công việc này.
- Hệ sinh thái thích hợp: **Amazon Quick** kết nối với các hệ sinh thái phổ biến như **Microsoft (PowerBI, Word, Outlook, Teams)** và **Google (Gmail, Calender)** thông qua **platform Agent**, cho phép người dùng tự xây dựng các Agent phục vụ mục đích cá nhân hoặc doanh nghiệp.
- Các tính năng nổi bật:
    - **BI (Business Intelligence)**: Tự động phân tích chuyên sâu khi nhận dữ liệu đầu vào.
    - **Inside & Chat**: Cho phép tương tác trực tiếp với dữ liệu để hiểu thông tin.
    - **Automation**: Tự động hóa hoàn toàn quy trình công việc thông qua **automation flow**.
- Demo thực tế: Phần demo cho thấy khả năng nhập dữ liệu Excel để tạo Dashboard tự động và yêu cầu AI tóm tắt nội dung cuộc họp từ file record, giúp người dùng không chuyên về kỹ thuật cũng có thể xử lý dữ liệu phức tạp một cách dễ dàng.

#### Chủ Đề 3: From Edge To Origin: CloudFront as Your Foundation - Thinh Nguyen

Chủ đề này tập trung vào vai trò của **Amazon CloudFront** không chỉ là dịch vụ CDN truyền thống mà còn là nền tảng bảo mật, tối ưu hóa ứng dụng toàn diện.

Các nội dung chính bao gồm:

1. Khả năng bảo mật nâng cao:
- **VPC Private Origin**: Tạo đường truyền riêng biệt từ **CloudFront** vào **private subnet**, giúp ẩn hạ tầng **backend** khỏi internet công cộng.
- **Mutual TLS**: Yêu cầu xác thực chứng chỉ từ cả hai phía (client và server), phù hợp cho các hệ thống tài chính hoặc nội dung bản quyền.
- **Chặn tấn công theo khu vực/IP**: Giảm tải cho server bằng cách chặn các truy cập độc hại ngay tại lớp **Edge** trước khi chúng chạm tới **Origin**.

2. Tối ưu hóa hiệu năng:
- **Content Compression**: Tính năng nén nội dung giúp giảm dung lượng gói tin đáng kể (lên đến 82%), cải thiện tốc độ tải trang.
- **Giảm tải GPU cho EC2**: CloudFront thay thế EC2 xử lý các tác vụ như bắt tay TCP, TLS, giúp server chỉ tập trung xử lý logic nghiệp vụ.

3. Catching đa tầng: Cơ chế lưu trữ thông tin tại các **Point of Presence (PoP) giúp phân phối dữ liệu hiệu quả, giảm độ trễ cho người dùng cuối dù ở bất kỳ đâu trên thế giới.

#### Chủ đề 4: 36 hrs with LotusHacks – Building UTMorpho from Idea to Reality - Team VIB

Chủ đề này kể về hành trình 36 giờ xây dựng sản phẩm tại cuộc thi **Hackathon** lớn nhất Việt Nam. Các nội dung chính bao gồm:

1. **Ý tưởng sản phẩm (UTMorpho)**: Nhóm tập trung giải quyết bài toán lãng phí thời gian và token khi người sử dụng AI để thiết kể UI. Thay vì phải yêu cầu AI tạo lại toàn bộ giao diện mỗi khi muốn chỉnh sửa chi tiết, **UTMorpho** cho phép chỉnh sửa trực tiếp trên giao diện đã được tạo.

2. Kiến trúc hệ thống: Nhóm sử dụng kiến trúc **serverless** kết hợp với 3 Agent AI chuyên biệt để xử lý dữ liệu đầu vào:
- Agent 1: Phân tích hình ảnh/bản vẽ phác thảo từ người dùng.
- Agent 2: Tạo layout, CSS và cấu trúc thành phần.
- Agent 3: Hoàn thiện code giao diện dựa trên yêu cầu.

3. Thách thức gặp phải:
- Giới hạn Token: Việc sử dụng AI liên tục dẫn đến việt báo lỗi **limit** giữa chừng.
- Over-generation: AI tự ý tạo thêm những tính năng không cần thiết, gây khó khăn trong việc kiểm soát code.
- Kiệt sức: Áp lực thời gian và mệt mỏi vào lúc 4-5 giờ sáng khiến nhóm phải thay đổi chiến thuật, tập trung tối ưu trải nghiệm chỉnh sửa thay vì thêm quá nhiều tính năng.

4. Bài học kinh nghiệm: Nhóm nhấn mạnh tầm quan trọng của việc giữ cho ý tưởng đơn giản, tập trung vào giải quyết một vấn đề cụ thể thay vì phải nhồi nhét nhiều tính năng phức tạp trong thời gian ngắn.

#### Chủ Đề 5: Non-Determinism of "Deterministic" LLM Settings - Duc Dao

Chủ đề này đi sâu vào việc giải mã bản chất xác xuất của các mô hình ngôn ngữ lớn (LLM) và những lầm tưởng về tính *định tính* của chúng trong kỹ thuật phần mềm.

Các nội dung chính bao gồm:

1. Bản chất của LLM: LLM về cơ bản là một **probabilistic engine**. Việc tạo ra từ tiếp theo dựa trên việc chấm điểm và xếp hạng các từ trong từ điển, thay vì là một quy trình logic cứng nhắc.

2. Lầm tưởng về *Temperature = 0*: Nhiều lập trình viên cho rằng đặt *temperature = 0* sẽ giúp mô hình trở nên hoàn toàn định tính (đầu vào giống nhau thì đâu ra luôn luôn giống nhau). Tuy nhiên, thực tế là ngay khi cả *temperature = 0*, vẫn tồn tại sự khác biệt nhỏ giữa các lần chạy cho bản chất của GPU và thư viện cung cấp.

3. Thách thức trong production: 
- Sự khác biệt trong kết quả đầu ra có thể ảnh hưởng đến các ứng dụng quan trọng, nơi cần sự nhất quán tuyệt đổi.
- Một số mô hình khi đặt *temperator = 0* (chế dộ *greaddy decoding*) có thể bị lặp từ.

4. Chiến lược giảm thiểu:
- Thử nghiệm và kiểm thử: Nhấn mạnh tầm quan trọng của việc kiểm thử sâu và rộng để đảm bảo hệ thống có thể xử lý các output không mong muốn.
- Thiết kế **Downstream**: Các services nhận kết quả từ LLM cần được thiết kế để xử lý linh hoạt thay vì mong đợi một kết quả hoàn hảo.
- Tham số tối ưu: Đôi khi đặt *temperature = 0.1* thay vì 0 lại cho kết quả ổn định hơn đối với một số mô hình, giúp tránh lỗi lặp từ.
- Sử dụng tính năng chuyên biệt: Tận dụng các tham số như **JSON mode** của các nhà cung cấp API để buộc mô hình tuân thủ định dạng dữ liệu.

5. Thông điệp cốt lõi: Luôn đọc kỹ **official documentation** của từng model cụ thể thay vì áp dụng kinh nghiệm chung, vì cách vận hành của mỗi model có thể khác nhau.

#### Chủ Đề 6: Enterprise-Grade Multi-Agent System: The Case of Startup Credit Scoring - Vy Lam

Đối với mình thì đây là một chủ đề nổi bật nhất. Chủ đề này tập trung vào việc thiết kế hệ thống đa tác tử (multi-agent) cấp doanh nghiệp trong lĩnh vực đánh giá tín dụng cho Startup.

Các nội dung chính bao gồm:

1. Thách thức nghiệp vụ: Các mô hình tín dụng truyền thống thông thường không phù hợp với Startup vì thiếu lịch sử tài chính 3 năm, thiếu tài sản thế chấp vật lý và thiếu hồ sơ tín dụng. Hệ thống cần khai thác các chiều dữ liệu khác như tài sản trí tuệ, khả năng tăng trưởng và thông ti người sáng lập.

2. Kiến trúc Multi-Agent: 

- Thay vì dùng một agent duy nhất, vốn dễ bị giới hạn bởi context window và khó đảm nhiệm nhiều chuyên môn cùng lúc thì hệ thống được chia thành các tác tử chuyên biệt: **Financial Analyst**, **Research Agent**, **Team Evaluator**, và **Risk Assessor**.
- Hệ thống sử dụng một **Manager Agent** để điều phối nhiệm vụ và tổng hợp kết quả.

3. Tiêu chuẩn doanh nghiệp:
- **Security & Compliance**: Nhấn mạnh tầm quan trọng của việc tuân thủ các quy định bảo mật, bảo về dữ liệu khách hàng và tránh các lỗi **MCP attack vector**.
- **Audit Trail**: Mọi quyết định của AI cần được lưu vết để phục vụ kiểm tra, đặc biệt là khi đối mặt với cơ quan quản lý.
- **Human-in-the-loop**: AI chỉ đóng vai trò hỗ trợ, con người đóng vai trò review và phê duyệt cuối cùng để chịu trách nhiệm cho các quyết định giải ngân.

4. Kinh nghiệm triển khai:
- Quy trình gồm các giai đoạn: Build Core -> Internal Testing -> SIT (System Integration Testing) -> UAT (User Acceptance Testing) -> Pilot -> Scale

5. Lời khuyên kỹ thuật:
- Tập trung vào kỹ năng backedn thay vì chỉ biết mỗi AI, vì dữ liệu và cơ sở dữ liệu an toàn mới là nền tảng.
- Sử dụng **Infrastructure as Code** (Terraform) để quản lý hạ tầng thay vì thao tác thủ công, giúp dễ dàng sao chép và quản lý phiên bản.

6. Thông điệp cốt lõi: Hệ thống không chỉ cần chạy được, mà còn phải đảm bảo tính an toàn, đáng tin cậy và phục vụ mọi người.

### Những Gì Học Được

Sau khi tham gia sự kiện, em đã học được nhiều kiến thức và góc nhìn thực tế về xu hướng phát triển của Cloud Computing và AI trong doanh nghiệp, cụ thể:
- Hiểu được rằng AI không thay thế hoàn toàn lập trình viên mà đang làm thay đổi cách phát triển phần mềm. Điều quan trọng không chỉ là biết sử dụng AI mà còn phải có kiến thức chuyên môn và khả năng giải quyết bài toán thực tế.
- Nhận thức được tầm quan trọng của **Prompt Engineering**, đặc biệt là việc cung cấp đầy đủ ngữ cảnh (context) để AI có thể đưa ra kết quả chính xác và phù hợp với yêu cầu.
- Hiểu thêm về cách doanh nghiệp ứng dụng các dịch vụ AI trên AWS để xây dựng trợ lý AI, tự động hóa quy trình làm việc và hỗ trợ ra quyết định.
- Nắm được các tính năng mới của **Amazon CloudFront** trong việc tăng cường bảo mật, tối ưu hiệu năng và giảm tải cho hạ tầng backend, thay vì chỉ xem đây là một dịch vụ CDN truyền thống.
- Học được kinh nghiệm xây dựng sản phẩm AI trong môi trường Hackathon, đặc biệt là cách tối ưu thời gian, lựa chọn phạm vi chức năng phù hợp và tập trung giải quyết đúng vấn đề của người dùng.
- Hiểu rõ hơn về bản chất xác suất của các mô hình ngôn ngữ lớn (LLM), những hạn chế của việc coi LLM là hoàn toàn "deterministic", cũng như các phương pháp giảm thiểu sự khác biệt trong kết quả đầu ra khi triển khai thực tế.
- Tiếp cận tư duy thiết kế **Multi-Agent System** dành cho doanh nghiệp, trong đó mỗi Agent đảm nhiệm một vai trò chuyên biệt và được điều phối bởi một Agent trung tâm nhằm nâng cao hiệu quả xử lý.
- Nhận thức được rằng khi triển khai AI trong môi trường doanh nghiệp, các yếu tố như bảo mật, khả năng kiểm toán (Audit Trail), Human-in-the-loop và tuân thủ quy định còn quan trọng không kém bản thân mô hình AI.
- Hiểu được vai trò của **Infrastructure as Code (Terraform)** trong việc quản lý hạ tầng, giúp tự động hóa triển khai, quản lý phiên bản và đảm bảo khả năng mở rộng của hệ thống.

### Ứng Dụng Vào Công Việc

Những kiến thức thu được từ sự kiện sẽ là nền tảng quan trọng cho quá trình học tập cũng như định hướng nghề nghiệp của em trong tương lai.

Trong thời gian tới, em dự định:
- Tiếp tục nghiên cứu và thực hành các dịch vụ AI trên nền tảng **Amazon Web Services (AWS)**, đặc biệt là các giải pháp phục vụ xây dựng ứng dụng Generative AI.
- Áp dụng các nguyên tắc **Prompt Engineering** để nâng cao chất lượng khi sử dụng các mô hình ngôn ngữ lớn trong học tập và phát triển phần mềm.
- Tìm hiểu sâu hơn về **Amazon CloudFront**, các giải pháp bảo mật Edge và tối ưu hiệu năng để áp dụng vào các dự án triển khai website hoặc hệ thống trên AWS.
- Thực hành xây dựng các hệ thống **Multi-Agent** nhằm giải quyết những bài toán phức tạp, đồng thời kết hợp với các quy trình Human-in-the-loop để nâng cao độ tin cậy của hệ thống.
- Tiếp tục sử dụng **Terraform** và các công cụ Infrastructure as Code trong các dự án Cloud để tự động hóa quá trình triển khai và quản lý hạ tầng.
- Chú trọng hơn đến việc xây dựng các dự án thực tế thay vì chỉ học lý thuyết, từ đó tạo ra sản phẩm có thể chứng minh năng lực khi tham gia các chương trình thực tập hoặc ứng tuyển vào doanh nghiệp.
- Không chỉ tập trung vào AI mà còn tiếp tục phát triển kiến thức về Backend, Cloud Computing, DevOps và System Design để có nền tảng kỹ thuật vững chắc phục vụ cho việc xây dựng các hệ thống AI trong môi trường doanh nghiệp.

### Trải Nghiệm Trong Sự Kiện

Sự kiện được tổ chức chuyên nghiệp với nhiều phiên chia sẻ có tính thực tiễn cao, tập trung vào những vấn đề mà các doanh nghiệp đang quan tâm trong lĩnh vực Cloud Computing và AI. Không khí chương trình diễn ra sôi nổi với sự tham gia của nhiều kỹ sư, chuyên gia và các bạn sinh viên có cùng đam mê công nghệ, tạo điều kiện thuận lợi để giao lưu và học hỏi.

Điểm em ấn tượng nhất là các diễn giả không chỉ giới thiệu lý thuyết mà còn chia sẻ nhiều kinh nghiệm thực tế trong quá trình phát triển sản phẩm, triển khai hệ thống và giải quyết các vấn đề phát sinh trong môi trường production. Đặc biệt, phần chia sẻ về Multi-Agent System, CloudFront và kinh nghiệm tham gia Hackathon đã giúp em có cái nhìn rõ ràng hơn về cách các công nghệ AI được ứng dụng trong doanh nghiệp.

Thông qua sự kiện, em không chỉ tiếp thu thêm nhiều kiến thức chuyên môn mà còn hiểu rõ hơn những kỹ năng mà doanh nghiệp đang tìm kiếm ở một kỹ sư Cloud hoặc AI. Đây là một trải nghiệm ý nghĩa, giúp em có thêm động lực để tiếp tục học tập, hoàn thiện kỹ năng chuyên môn và chuẩn bị tốt hơn cho định hướng nghề nghiệp trong lĩnh vực Cloud Computing, DevOps và Trí tuệ nhân tạo.

### Hình Ảnh Minh Chứng Tham Gia Sự Kiện

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_1.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_2.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_3.png)

- Dưới đây là một số hình ảnh trong sự kiện được chụp từ các anh chị **Admin** trong **AWS Study Group**:

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_4.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_5.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_6.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_7.png)

![Event Participated](/workshop-fcaj-intern/images/4-EventParticipated/4.2-Event2/event_8.png)