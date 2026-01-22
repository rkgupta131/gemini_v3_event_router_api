# data/questionnaire_config.py
"""
MCQ questionnaire configurations for different page types.
These questions help gather specific requirements when user input is vague.
"""

QUESTIONNAIRES = {
    "landing_page": {
        "questions": [
            {
                "id": "industry",
                "question": "What industry/category is this landing page for?",
                "type": "radio",
                "options": [
                    "SaaS / Software Product",
                    "E-commerce / Online Store",
                    "Agency / Services",
                    "Education / Course",
                    "Health & Wellness",
                    "Real Estate",
                    "Finance / Fintech",
                    "Event / Webinar",
                    "Mobile App",
                    "Other"
                ]
            },
            {
                "id": "primary_goal",
                "question": "What's the primary goal of this landing page?",
                "type": "radio",
                "options": [
                    "Lead Generation (Capture emails/contacts)",
                    "Product Launch / Announcement",
                    "Event Registration / Sign-ups",
                    "Free Trial / Demo Request",
                    "Direct Sales / Purchase",
                    "Download (Ebook, App, Resource)",
                    "Newsletter Subscription",
                    "Consultation Booking"
                ]
            },
            {
                "id": "target_audience",
                "question": "Who is your target audience?",
                "type": "radio",
                "options": [
                    "B2B (Businesses)",
                    "B2C (Consumers)",
                    "Developers / Technical",
                    "Students / Educators",
                    "Professionals / Executives",
                    "General Public",
                    "Small Business Owners"
                ]
            },
            {
                "id": "design_style",
                "question": "What design style do you prefer?",
                "type": "radio",
                "options": [
                    "Modern & Minimal",
                    "Bold & Colorful",
                    "Professional & Corporate",
                    "Creative & Artistic",
                    "Tech / Startup Vibe"
                ]
            },
            {
                "id": "features",
                "question": "Which features do you want to include?",
                "type": "multiselect",
                "options": [
                    "Hero Video/Animation",
                    "Customer Testimonials",
                    "Pricing Table",
                    "FAQ Section",
                    "Product Demo/Screenshots",
                    "Trust Badges/Logos",
                    "Live Chat Widget",
                    "Social Proof Counter"
                ]
            }
        ]
    },
    
    "crm_dashboard": {
        "questions": [
            {
                "id": "business_type",
                "question": "What type of business is this CRM for?",
                "type": "radio",
                "options": [
                    "Marketing Agency",
                    "Sales Team",
                    "Real Estate",
                    "Consulting Firm",
                    "E-commerce Business",
                    "B2B Services",
                    "Freelancer/Solopreneur"
                ]
            },
            {
                "id": "team_size",
                "question": "How large is your team?",
                "type": "radio",
                "options": [
                    "Solo (Just me)",
                    "Small (2-10 people)",
                    "Medium (11-50 people)",
                    "Large (50+ people)"
                ]
            },
            {
                "id": "key_features",
                "question": "What are your most important CRM features?",
                "type": "multiselect",
                "options": [
                    "Lead Management",
                    "Deal Pipeline Tracking",
                    "Activity Timeline",
                    "Email Integration",
                    "Task Management",
                    "Reporting & Analytics",
                    "Contact Segmentation",
                    "Document Storage"
                ]
            },
            {
                "id": "integration_needs",
                "question": "Do you need integrations?",
                "type": "multiselect",
                "options": [
                    "Email (Gmail, Outlook)",
                    "Calendar",
                    "Spreadsheets",
                    "Payment Processing",
                    "Marketing Tools",
                    "No integrations needed"
                ]
            }
        ]
    },
    
    "ecommerce_fashion": {
        "questions": [
            {
                "id": "store_type",
                "question": "What type of fashion products do you sell?",
                "type": "radio",
                "options": [
                    "Streetwear / Urban Fashion",
                    "Luxury / High-End Fashion",
                    "Casual / Everyday Wear",
                    "Sportswear / Activewear",
                    "Accessories / Jewelry",
                    "Sustainable / Eco Fashion"
                ]
            },
            {
                "id": "target_market",
                "question": "Who is your target market?",
                "type": "radio",
                "options": [
                    "Gen-Z (18-24)",
                    "Millennials (25-40)",
                    "Young Professionals",
                    "Premium/Luxury Buyers",
                    "Budget-Conscious Shoppers"
                ]
            },
            {
                "id": "store_features",
                "question": "Which e-commerce features do you need?",
                "type": "multiselect",
                "options": [
                    "Product Filters (Size, Color, Price)",
                    "Wishlist / Favorites",
                    "Size Guide",
                    "Product Reviews",
                    "Quick View",
                    "Stock Availability Alerts",
                    "Gift Cards",
                    "Referral Program"
                ]
            },
            {
                "id": "vibe",
                "question": "What's the vibe/aesthetic?",
                "type": "radio",
                "options": [
                    "Edgy & Bold",
                    "Minimalist & Clean",
                    "Luxury & Elegant",
                    "Fun & Playful",
                    "Earthy & Natural"
                ]
            }
        ]
    },
    
    "student_portfolio": {
        "questions": [
            {
                "id": "field",
                "question": "What field are you studying/working in?",
                "type": "radio",
                "options": [
                    "Computer Science / Engineering",
                    "Design / UX/UI",
                    "Business / Marketing",
                    "Data Science / Analytics",
                    "Creative Arts / Media",
                    "Research / Academia",
                    "Other"
                ]
            },
            {
                "id": "career_stage",
                "question": "What stage are you at?",
                "type": "radio",
                "options": [
                    "Current Student",
                    "Recent Graduate",
                    "Looking for Internship",
                    "Looking for Full-Time Job",
                    "Career Switch"
                ]
            },
            {
                "id": "showcase_items",
                "question": "What do you want to showcase?",
                "type": "multiselect",
                "options": [
                    "Academic Projects",
                    "Work Experience",
                    "Technical Skills",
                    "Certifications",
                    "Research Papers",
                    "Side Projects",
                    "Open Source Contributions",
                    "Awards & Achievements"
                ]
            }
        ]
    },
    
    "service_marketplace": {
        "questions": [
            {
                "id": "service_category",
                "question": "What type of services will be offered?",
                "type": "radio",
                "options": [
                    "Education / Tutoring",
                    "Home Services (Cleaning, Repairs)",
                    "Professional Services (Legal, Accounting)",
                    "Creative Services (Design, Writing)",
                    "Health & Wellness",
                    "Event Services",
                    "Transportation / Delivery"
                ]
            },
            {
                "id": "booking_type",
                "question": "How should booking work?",
                "type": "radio",
                "options": [
                    "Instant Booking (Immediate confirmation)",
                    "Request to Book (Provider approves)",
                    "Quote-Based (Provider sends estimate)",
                    "Scheduling Only (No payment)"
                ]
            },
            {
                "id": "marketplace_features",
                "question": "Which marketplace features do you need?",
                "type": "multiselect",
                "options": [
                    "Provider Profiles & Verification",
                    "Reviews & Ratings",
                    "In-App Messaging",
                    "Payment Processing",
                    "Calendar/Availability",
                    "Location/Map Search",
                    "Dispute Resolution",
                    "Commission Management"
                ]
            }
        ]
    },
    
    "digital_product_store": {
        "questions": [
            {
                "id": "product_type",
                "question": "What type of digital products are you selling?",
                "type": "radio",
                "options": [
                    "E-books / Guides",
                    "Notion Templates",
                    "Design Assets (Fonts, Icons, Templates)",
                    "Online Courses / Video Content",
                    "Software / Tools",
                    "Music / Audio",
                    "Photos / Stock Images"
                ]
            },
            {
                "id": "pricing_model",
                "question": "What's your pricing model?",
                "type": "radio",
                "options": [
                    "One-Time Purchase",
                    "Tiered Pricing (Standard/Extended License)",
                    "Subscription (Monthly/Annual)",
                    "Freemium (Free + Paid)",
                    "Pay What You Want"
                ]
            },
            {
                "id": "delivery_features",
                "question": "Which features do you need?",
                "type": "multiselect",
                "options": [
                    "Secure File Delivery",
                    "License Management",
                    "Automatic Updates",
                    "Customer Library/Dashboard",
                    "Preview/Demo Access",
                    "Affiliate Program",
                    "Bundle Discounts"
                ]
            }
        ]
    },
    
    "generic": {
        "questions": [
            {
                "id": "purpose",
                "question": "What's the main purpose of your website?",
                "type": "radio",
                "options": [
                    "Business/Marketing",
                    "Personal Blog",
                    "Portfolio",
                    "Information/Documentation",
                    "Community/Forum",
                    "Other"
                ]
            },
            {
                "id": "key_pages",
                "question": "Which pages do you need?",
                "type": "multiselect",
                "options": [
                    "Home Page",
                    "About Page",
                    "Contact Page",
                    "Services/Products Page",
                    "Blog",
                    "Gallery",
                    "Testimonials"
                ]
            }
        ]
    }
}


def get_questionnaire(page_type_key: str):
    """Get questionnaire for a specific page type."""
    return QUESTIONNAIRES.get(page_type_key, QUESTIONNAIRES.get("generic"))


def has_questionnaire(page_type_key: str):
    """Check if a page type has a questionnaire."""
    return page_type_key in QUESTIONNAIRES






