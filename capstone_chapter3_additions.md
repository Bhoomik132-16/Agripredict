# Chapter 3: Design Implementation — Advanced Feature Additions

## 3.X — Live Weather Integration, CNN Disease Classifier & LLM Platform Assistant

The AgriPredict platform was enhanced with three production-grade features to strengthen its AI-driven agricultural intelligence capabilities.

**OpenWeatherMap API Integration**: A RESTful endpoint (`/api/get-weather`) was implemented to fetch real-time meteorological data — temperature (°C), humidity (%), and rainfall (mm) — using latitude/longitude or city name parameters. The integration includes graceful fallback to default values when network connectivity or API key availability is compromised, ensuring uninterrupted user experience.

**CNN Crop Disease Classifier**: A Convolutional Neural Network pipeline leveraging PyTorch's MobileNetV2 (pretrained on ImageNet) was integrated for automated crop leaf disease detection via the `/api/predict-disease` endpoint. The system accepts sanitized image uploads, processes them through standard ImageNet normalization transforms, and maps predictions to 12 common crop diseases with corresponding treatment recommendations. A singleton pattern ensures model efficiency across concurrent requests.

**Gemini LLM Chatbot Assistant**: An intelligent conversational assistant powered by Google's Gemini 2.0 Flash model was deployed at `/api/chat`. The chatbot is context-trained through a comprehensive system prompt encoding AgriPredict's SCM pipeline stages (Paid_OrderPlaced → SCM_Managed → Finalized), role-specific guidance for Farmers and Vendors, Razorpay-style checkout procedures, and the automated 30% commission policy. Both disease predictions and chat interactions are persistently logged in SQLite tables (`disease_logs`, `chat_history`) for analytics and audit compliance.
