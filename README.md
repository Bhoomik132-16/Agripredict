# 🌾 AgriPredict: Comprehensive B2B Agri-Tech & AI Ecosystem 🇮🇳

**AgriPredict** is an enterprise-grade, end-to-end B2B Agricultural Intelligence platform designed to bridge the gap between Indian farmers, wholesale buyers/vendors, and supply chain managers. By combining **Random Forest Machine Learning**, **Convolutional Neural Network (CNN) Deep Learning**, **8-Language Localization**, an **Integrated B2B Marketplace**, a **Razorpay-Style Payment Gateway**, and **3-Stage Supply Chain Management (SCM)**, AgriPredict empowers agricultural stakeholders with data-driven decision-making.

---

## 📌 Executive Overview & Core Problem Statement

Traditional Indian agriculture suffers from critical inefficiencies:
1. **Unpredictable Crop Yields**: Farmers lack scientific guidance on soil nutrients (N-P-K), pH balance, and regional climate conditions.
2. **Crop Diseases & Yield Loss**: Undetected leaf fungal and bacterial blights cause massive crop losses without early diagnostic guidance.
3. **Language & Accessibility Barriers**: Agricultural tools often cater only to English speakers, excluding regional farming communities across India.
4. **Middlemen Exploitation**: Lack of direct B2B market connectivity reduces farmer profitability.

**AgriPredict resolves these challenges** through a single unified digital dashboard.

---

## 🌟 Comprehensive Technical Feature Breakdown

### 1. 🤖 Machine Learning Crop Recommendation & Yield Predictor Engine
- **Algorithm**: Scikit-Learn **RandomForest Classifier & Regressor** pipeline.
- **Input Parameters**:
  - **Soil Nutrients**: Nitrogen (N: 0–140 kg/ha), Phosphorus (P: 0–145 kg/ha), Potassium (K: 0–205 kg/ha).
  - **Soil Property**: pH Level (3.5 – 10.0).
  - **Climate Factors**: Temperature (°C), Relative Humidity (%), Annual Rainfall (mm).
  - **Location**: Selected Indian State (Supports all 28 states).
  - **Land Size**: Cultivation Area in Hectares.
- **Output Intelligence**:
  - Recommends the optimal crop suitable for the specific soil and weather profile.
  - Predicts estimated total yield in **Quintals** and **Metric Tons**.
  - Calculates estimated market revenue based on regional commodity price trends.

---

### 2. 🔬 CNN Deep Learning Leaf Disease Classifier & Diagnostics
- **Architecture**: **MobileNetV2** Convolutional Neural Network (CNN) fine-tuned for leaf pathology classification.
- **Input Processing**: Image resize to $224 \times 224 \times 3$ RGB tensor, normalized using ImageNet mean & standard deviation.
- **Diagnostic Output**:
  - Real-time **Disease Identification** (e.g., Fungal Leaf Blight, Powdery Mildew, Leaf Rust, Late Blight).
  - **AI Confidence Score Matrix** (e.g., `94.8% Confidence`).
  - **Pathology & Treatment Advice**: Actionable remedies specifying exact chemical formulations (e.g., *Mancozeb 2.5g/L*, *Propiconazole*, *Streptocycline*).
- **📸 Built-In Demo Sample Generator**: Automatically creates high-resolution sample infected leaf images (`leaf_blight_sample.jpg`, `powdery_mildew_sample.jpg`, `leaf_rust_sample.jpg`) inside `static/` for live offline reviewer demonstrations.

---

### 3. 🌐 Multilingual Globalization Engine (8 Languages)
The platform features an interactive language selection dropdown (`#cnn-lang-select`) supporting 8 regional & international languages:
1. 🇬🇧 **English** (`en`)
2. 🇮🇳 **हिंदी - Hindi** (`hi`)
3. 🚩 **मराठी - Marathi** (`mr`)
4. 🌾 **ગુજરાતી - Gujarati** (`gu`)
5. 🌾 **ਪੰਜਾਬੀ - Punjabi** (`pa`)
6. 🌾 **தமிழ் - Tamil** (`ta`)
7. 🌾 **తెలుగు - Telugu** (`te`)
8. 🌾 **বাংলা - Bengali** (`bn`)

**Dynamic UI Translation Capabilities**:
- Translates Panel Titles, Subtitles, Upload Labels, and Scan Buttons.
- Translates Crop Names into regional scripts (e.g., *Potato* → *आलू* in Hindi, *बटाटा* in Marathi, *બટાકા* in Gujarati).
- Dynamically updates the **Pre-Predicted Crop Disease Vulnerability Notice** in the target language.

---

### 4. 🛡️ State-Aware Pre-Predicted Crop Disease Vulnerability Warning
- **Contextual Intelligence**: Analyzes the active **State** and **Selected Crop** to alert farmers to region-specific seasonal pathology risks (e.g., Late Blight in Potato for Maharashtra or Yellow Rust in Wheat for Punjab).
- **Real-Time Reactive UI**: Instantly updates whenever the farmer switches states, selects different crops, or toggles the language dropdown.

---

### 5. 🛒 B2B Farmer-to-Vendor Marketplace & Direct Listing Workflow
- **1-Click AI Listing Conversion**: Farmers can directly convert yield predictions into active marketplace listings without manual re-entry.
- **Vendor Marketplace Hub**: Vendors and wholesale buyers can search available listings by crop name, price, quantity, and state.
- **Direct Buying**: Enables transparent transactions directly between agricultural sellers and buyers.

---

### 6. 💳 Integrated ePayment Gateway & 3-Stage Supply Chain Management (SCM)
- **Razorpay-Style Checkout**: Simulates secure digital payments via **UPI**, **Credit/Debit Cards**, and **Net Banking**.
- **3-Stage Order Lifecycle**:
  1. **`Paid_OrderPlaced`**: Vendor completes payment; order enters system queue.
  2. **`SCM_Managed`**: Admin manages logistics, quality inspection, and dispatch.
  3. **`Finalized`**: Successful delivery; triggers automated **30% Platform Commission** deduction & seller payout.

---

### 7. 📊 Interactive Admin Control Center, Marketing Analytics & CRM
- **Marketing Strategy Analytics**: Visualizes platform user reach (Facebook 12k+, Instagram 8k+, Direct Marketing) using real-time interactive **Pie Charts** with percentage calculations.
- **CRM Support Ticket Hub**: Integrates landing page "Say Hello" contact submissions directly into the System Admin dashboard for issue resolution.
- **User & Order Oversight**: System Admins have full CRUD capability over users, marketplace listings, and order statuses.

---

## 📂 Complete Project Directory Map

```
Agri predict/
├── app.py                            # Main Flask application (Routes, API handlers, Authentication)
├── ml_pipeline.py                    # Scikit-Learn Machine Learning pipeline & model training logic
├── database.py                       # SQLite database initialization & schema management
├── seed_db.py                        # Populates DB with realistic Indian agricultural sample data
├── requirements.txt                  # Python package dependencies
├── CROP_PREDICTION_MATH.md           # Mathematical formula guide for manual yield calculation verification
├── README.md                         # Comprehensive documentation (this file)
├── models/                           # Saved ML model artifacts (.joblib files)
├── templates/
│   ├── dashboard.html                # Main User Dashboard (Yield Predictor, CNN Classifier, Marketplace)
│   ├── landing.html                  # Public Landing Page with platform reach & contact forms
│   └── login.html                    # Authentication Page (Login / Signup)
├── static/
│   ├── css/                          # Custom CSS styles (Glassmorphism design tokens)
│   ├── js/                           # Frontend interactive logic & Chart.js scripts
│   ├── leaf_blight_sample.jpg        # Demo leaf image asset for CNN testing
│   ├── powdery_mildew_sample.jpg     # Demo leaf image asset for CNN testing
│   └── leaf_rust_sample.jpg          # Demo leaf image asset for CNN testing
└── uploads/                          # Directory storing user-uploaded leaf inspection images
```

---

## 🔌 API Endpoint Documentation

| Method | Endpoint | Description | Payload Example / Response |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/predict` | Predicts recommended crop & estimated yield | `{"N": 90, "P": 40, "K": 40, "ph": 6.5, "state": "Maharashtra", "hectares": 2}` |
| **POST** | `/api/predict_disease` | CNN image analysis for leaf disease | Form-data image upload (`leaf_image.jpg`) |
| **POST** | `/api/create_listing` | Converts yield prediction into market listing | `{"crop_name": "Wheat", "quantity_quintals": 50, "price_per_quintal": 2200}` |
| **POST** | `/api/create_order` | Simulates payment & creates SCM order | `{"listing_id": 1, "payment_method": "UPI", "transaction_id": "TXN9982"}` |
| **POST** | `/api/update_order_status` | Updates SCM stage (`Paid_OrderPlaced` -> `Finalized`) | `{"order_id": 1, "new_status": "Finalized"}` |
| **POST** | `/api/support` | Submits contact ticket from landing page | `{"name": "Ramesh", "email": "ramesh@farm.com", "message": "Help with listing"}` |

---

## 📐 Mathematical Yield Verification Formulas

To ensure complete scientific transparency, AgriPredict provides manual verification formulas in `CROP_PREDICTION_MATH.md`:

1. **Base Yield Factor ($Y_{base}$)**:
   $$Y_{base} = \left(\frac{N + P + K}{300}\right) \times 25 \text{ quintals/hectare}$$

2. **Soil pH Multiplier ($M_{pH}$)**:
   $$M_{pH} = 1.0 - |pH - 6.5| \times 0.1$$

3. **Total Estimated Harvest ($Y_{total}$)**:
   $$Y_{total} = Y_{base} \times M_{pH} \times \text{Hectares}$$

---

## 🚀 Installation & Execution Guide

### Step 1: Clone & Navigate to Project Directory
```bash
cd "c:\Users\mulra\OneDrive\Desktop\Agri predict"
```

### Step 2: Install Python Dependencies
```bash
pip install flask pandas scikit-learn joblib pillow
```

### Step 3: Seed Database & Generate Demo Image Samples
```bash
python seed_db.py
```

### Step 4: Run Flask Development Server
```bash
python app.py
```

### Step 5: Access Platform in Web Browser
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials for Evaluation & Testing

| User Role | Account Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@agripredict.com` | `admin123` | Full SCM Control, Marketing Analytics, Ticket Hub |
| **Premium Farmer** | `rajesh@farm.com` | `farmer123` | Yield Prediction, CNN Disease Diagnostics, Listing Creation |
| **Verified Vendor** | `fresh@vendor.com` | `vendor123` | B2B Marketplace Search, Razorpay Checkout, Order Tracking |

---

© 2026 **AgriPredict AI Platform** | Designed & Built for Enterprise Demonstration & Capstone Evaluation 🌾
