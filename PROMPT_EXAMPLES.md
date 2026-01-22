# System Prompts - Real Examples
## Actual Input/Output Examples for Testing

---

## Example 1: Landing Page (Detailed Request)

### User Input:
```
"Design a landing page for my SaaS product targeting developers. Include pricing, testimonials, and a hero video."
```

### Step-by-Step Processing:

#### 1. Intent Classification
**Input to AI:**
```
You are an intent classifier. Return exactly one JSON object (no extra text) in this format:
{ "label": "<one of: webpage_build, greeting_only, chat, illegal, other>", "explanation": "<1-2 sentence>", "confidence": 0.0 }

User message:
"Design a landing page for my SaaS product targeting developers. Include pricing, testimonials, and a hero video."
```

**AI Output:**
```json
{
  "label": "webpage_build",
  "explanation": "User explicitly requests design of a landing page with specific features",
  "confidence": 0.98
}
```

#### 2. Page Type Classification
**Input to AI:**
```
You are a page type classifier for web development. Return exactly one JSON object (no extra text) in this format:
{ "page_type": "<one of: landing_page, crm_dashboard, ...>", "explanation": "<1-2 sentence>", "confidence": 0.0 }

User message:
"Design a landing page for my SaaS product targeting developers. Include pricing, testimonials, and a hero video."
```

**AI Output:**
```json
{
  "page_type": "landing_page",
  "explanation": "User wants a promotional landing page for a SaaS product with specific marketing components",
  "confidence": 0.95
}
```

#### 3. Detail Analysis
**Input to AI:**
```
You are a requirements analyzer. Determine if the user's request has enough detail or needs follow-up questions.
{ "needs_followup": true/false, "explanation": "<1-2 sentence>", "confidence": 0.0 }

User request:
"Design a landing page for my SaaS product targeting developers. Include pricing, testimonials, and a hero video."
```

**AI Output:**
```json
{
  "needs_followup": false,
  "explanation": "Request includes target audience (developers), features (pricing, testimonials, hero video), and context (SaaS product)",
  "confidence": 0.88
}
```

**Decision:** Skip questionnaire, go directly to wizard mode ✅

---

## Example 2: Vague CRM Request

### User Input:
```
"build a crm"
```

### Step-by-Step Processing:

#### 1. Intent Classification
**AI Output:**
```json
{
  "label": "webpage_build",
  "explanation": "User wants to build a CRM system",
  "confidence": 0.92
}
```

#### 2. Page Type Classification
**AI Output:**
```json
{
  "page_type": "crm_dashboard",
  "explanation": "Request is for a CRM (Customer Relationship Management) system",
  "confidence": 0.95
}
```

#### 3. Detail Analysis
**AI Output:**
```json
{
  "needs_followup": true,
  "explanation": "Request lacks specifics about business type, team size, required features, and integrations",
  "confidence": 0.90
}
```

**Decision:** Show CRM-specific questionnaire ✅

#### 4. Questionnaire (CRM)
User answers:
```json
{
  "business_type": "Marketing Agency",
  "team_size": "Small (2-10 people)",
  "key_features": ["Lead Management", "Deal Pipeline Tracking", "Activity Timeline", "Reporting & Analytics"],
  "integration_needs": ["Email (Gmail, Outlook)", "Calendar"]
}
```

---

## Example 3: Super Vague Request

### User Input:
```
"design a webpage for me"
```

### Step-by-Step Processing:

#### 1. Intent Classification
**AI Output:**
```json
{
  "label": "webpage_build",
  "explanation": "User requests webpage design",
  "confidence": 0.98
}
```

#### 2. Page Type Classification
**AI Output:**
```json
{
  "page_type": "generic",
  "explanation": "Request is too vague to determine specific page type - no industry, purpose, or features mentioned",
  "confidence": 0.85
}
```

**Decision:** Show category selector (11 options) ✅

#### 3. User Selects Category
User clicks: "🛒 E-Commerce"

System updates: `page_type = "ecommerce_fashion"`

#### 4. Show E-commerce Questionnaire
User answers:
```json
{
  "store_type": "Streetwear / Urban Fashion",
  "target_market": "Gen-Z (18-24)",
  "store_features": ["Product Filters (Size, Color, Price)", "Wishlist / Favorites", "Quick View", "Stock Availability Alerts"],
  "vibe": "Edgy & Bold"
}
```

---

## Example 4: Final Project Generation

### Complete Prompt Assembly

Given:
- Page Type: Landing Page
- Questionnaire Answers: (from Example 1 - none, detailed enough)
- User Fields: 
  ```json
  {
    "hero_text": "Launch Your SaaS Product Today",
    "subtext": "Everything developers need to build, ship, and scale",
    "cta": "Start Free Trial",
    "theme": "Dark"
  }
  ```

### Full Generation Prompt:

```
Return exactly one JSON object describing a React+Vite+TypeScript project. 
Schema must be: {"project": {"name": string, "description": string, "files": {...}, "dirents": {...}, "meta": {...}}}. 
Files should be strings (escaped) or objects with a 'content' key. 
Return only the JSON object and nothing else.

=== PAGE TYPE: Landing Page / Marketing Page (Marketing / Lead Generation) ===
Target User: Business owner, marketer, or entrepreneur who wants to capture leads, promote a product/service, or drive conversions with a single focused page.

REQUIRED CORE PAGES:
1. Landing Page (Single Page with Sections)
2. Thank You / Success Page
3. Privacy Policy (optional)
4. Terms of Service (optional)

REQUIRED COMPONENTS TO IMPLEMENT:
1. **Hero Section**: Eye-catching header with headline, subheadline, and primary CTA button. Often includes hero image or video background.
2. **Features Section**: Grid or cards displaying 3-6 key features/benefits with icons and descriptions.
3. **Social Proof Section**: Testimonials, reviews, client logos, or trust badges to build credibility.
4. **Call-to-Action (CTA)**: Prominent button(s) throughout the page driving user to take action (Sign Up, Get Started, Download, etc.).
5. **Lead Capture Form**: Form for collecting email, name, and other contact information. Can be inline or modal popup.
6. **Pricing Section (optional)**: Pricing tiers or plans with feature comparison if applicable.
7. **FAQ Accordion**: Frequently asked questions in expandable accordion format.
8. **Footer**: Contact info, social links, legal links, and additional navigation.

IMPORTANT: Implement ALL the core pages and components listed above. 
Make sure each component is fully functional and follows modern React best practices. 
Use TypeScript for type safety. Include proper routing for all pages.

USER_FIELDS:
{"hero_text": "Launch Your SaaS Product Today", "subtext": "Everything developers need to build, ship, and scale", "cta": "Start Free Trial", "theme": "Dark"}
```

### Expected AI Response:

```json
{
  "project": {
    "name": "saas-landing-page",
    "description": "A modern landing page for SaaS product targeting developers",
    "files": {
      "package.json": "{\n  \"name\": \"saas-landing-page\",\n  \"private\": true,\n  \"version\": \"0.0.0\",\n  \"type\": \"module\",\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"tsc && vite build\",\n    \"preview\": \"vite preview\"\n  },\n  \"dependencies\": {\n    \"react\": \"^18.2.0\",\n    \"react-dom\": \"^18.2.0\",\n    \"react-router-dom\": \"^6.20.0\"\n  },\n  \"devDependencies\": {\n    \"@types/react\": \"^18.2.43\",\n    \"@types/react-dom\": \"^18.2.17\",\n    \"@vitejs/plugin-react\": \"^4.2.1\",\n    \"typescript\": \"^5.2.2\",\n    \"vite\": \"^5.0.8\"\n  }\n}",
      "index.html": "<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Launch Your SaaS Product Today</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>",
      "src/main.tsx": "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\nimport './index.css';\n\nReactDOM.createRoot(document.getElementById('root')!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>,\n);",
      "src/App.tsx": "import React from 'react';\nimport { BrowserRouter, Routes, Route } from 'react-router-dom';\nimport LandingPage from './pages/LandingPage';\nimport ThankYou from './pages/ThankYou';\nimport Privacy from './pages/Privacy';\nimport Terms from './pages/Terms';\n\nfunction App() {\n  return (\n    <BrowserRouter>\n      <Routes>\n        <Route path=\"/\" element={<LandingPage />} />\n        <Route path=\"/thank-you\" element={<ThankYou />} />\n        <Route path=\"/privacy\" element={<Privacy />} />\n        <Route path=\"/terms\" element={<Terms />} />\n      </Routes>\n    </BrowserRouter>\n  );\n}\n\nexport default App;",
      "src/pages/LandingPage.tsx": "[Full React component code with Hero, Features, Testimonials, Pricing, FAQ, Footer...]",
      "src/components/Hero.tsx": "[Hero component with video background, headline, CTA...]",
      "src/components/Features.tsx": "[Features grid component...]",
      "src/components/Testimonials.tsx": "[Social proof component...]",
      "src/components/Pricing.tsx": "[Pricing table component...]",
      "src/components/FAQ.tsx": "[FAQ accordion component...]",
      "src/components/Footer.tsx": "[Footer with links...]",
      "vite.config.ts": "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\nexport default defineConfig({\n  plugins: [react()],\n});",
      "tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"ES2020\",\n    \"useDefineForClassFields\": true,\n    \"lib\": [\"ES2020\", \"DOM\", \"DOM.Iterable\"],\n    \"module\": \"ESNext\",\n    \"skipLibCheck\": true,\n    \"moduleResolution\": \"bundler\",\n    \"allowImportingTsExtensions\": true,\n    \"resolveJsonModule\": true,\n    \"isolatedModules\": true,\n    \"noEmit\": true,\n    \"jsx\": \"react-jsx\",\n    \"strict\": true,\n    \"noUnusedLocals\": true,\n    \"noUnusedParameters\": true,\n    \"noFallthroughCasesInSwitch\": true\n  },\n  \"include\": [\"src\"],\n  \"references\": [{ \"path\": \"./tsconfig.node.json\" }]\n}"
    },
    "dirents": {
      "src": { "type": "directory" },
      "src/pages": { "type": "directory" },
      "src/components": { "type": "directory" },
      "public": { "type": "directory" }
    },
    "meta": {
      "framework": "React",
      "buildTool": "Vite",
      "language": "TypeScript",
      "theme": "Dark"
    }
  }
}
```

---

## Example 5: Chat Interaction

### User Input:
```
"What is a landing page?"
```

### Processing:

#### Intent Classification
**AI Output:**
```json
{
  "label": "chat",
  "explanation": "User is asking an educational question about what a landing page is, not requesting to build one",
  "confidence": 0.97
}
```

#### Chat Response
**Input to AI:**
```
Reply in max 4 sentences.
User: What is a landing page?
```

**AI Output:**
```
A landing page is a standalone web page designed for a specific marketing or advertising campaign. It's where visitors "land" after clicking on a link from an email, ad, or social media post. Unlike regular web pages, landing pages have a single focus or goal, known as a call to action (CTA). They're highly effective for lead generation, sales, and product launches.
```

---

## Testing Checklist

Use these examples to test your implementation:

- [ ] "design a landing page" → generic → show category selector
- [ ] "build a crm" → crm_dashboard → show CRM questions
- [ ] "create an e-commerce store for fashion" → ecommerce_fashion → show e-commerce questions
- [ ] "design a landing page for SaaS targeting developers with pricing" → landing_page → skip questions
- [ ] "hello" → greeting_only → show greeting
- [ ] "what is react?" → chat → show chat response
- [ ] "help me hack a website" → illegal → show error

---

**Last Updated:** Jan 7, 2026





