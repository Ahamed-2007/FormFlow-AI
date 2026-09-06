"""Python port of includes/services.php."""


def formflow_services():
    return {
        "Income Certificate": {
            "category": "Certificates",
            "description": "Prepare an income-related certificate application with a clear, cautious checklist.",
            "questions": [
                {"key": "purpose", "label": "What are you applying for?", "type": "text", "placeholder": "Example: scholarship, fee support, or another application"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have address or residence proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "income", "label": "Do you have income-related supporting information?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "self_apply", "label": "Are you applying for yourself?", "type": "choice", "options": {"yes": "Yes", "no": "No, for someone else", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "address", "label": "Address or residence proof", "question": "address"},
                {"key": "income", "label": "Income-related supporting information", "question": "income"},
                {"key": "authority", "label": "Current authority requirements", "status": "verify"},
            ],
            "journey": ["Prepare information", "Apply through the relevant channel", "Verification", "Processing", "Outcome", "Follow-up or renewal if applicable"],
        },
        "Community Certificate": {
            "category": "Certificates",
            "description": "Organize your certificate preparation without assuming state-specific rules.",
            "questions": [
                {"key": "purpose", "label": "What will you use this certificate for?", "type": "text", "placeholder": "Example: education, employment, or another application"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have residence or address proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "supporting", "label": "Do you have supporting family or community information?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "address", "label": "Residence or address proof", "question": "address"},
                {"key": "supporting", "label": "Supporting information", "question": "supporting"},
                {"key": "authority", "label": "Current authority requirements", "status": "verify"},
            ],
            "journey": ["Prepare information", "Apply through the relevant channel", "Verification", "Processing", "Outcome", "Follow-up if applicable"],
        },
        "Residence Certificate": {
            "category": "Certificates",
            "description": "Get ready with residence information while keeping local requirements to verify.",
            "questions": [
                {"key": "purpose", "label": "What are you applying for?", "type": "text", "placeholder": "Example: education, employment, or local service"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have address or residence proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "history", "label": "Do you know the residence details the form asks for?", "type": "choice", "options": {"yes": "Yes", "no": "Not yet", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "address", "label": "Address or residence proof", "question": "address"},
                {"key": "history", "label": "Residence details", "question": "history"},
                {"key": "authority", "label": "Current authority requirements", "status": "verify"},
            ],
            "journey": ["Prepare residence information", "Apply through the relevant channel", "Verification", "Processing", "Outcome", "Follow-up if applicable"],
        },
        "Scholarship Application": {
            "category": "Education",
            "description": "Build a scholarship preparation checklist around your current information and documents.",
            "questions": [
                {"key": "scholarship", "label": "Which scholarship or education support are you applying for?", "type": "text", "placeholder": "Enter the name if you know it"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "education", "label": "Do you have current education or enrollment information?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "income", "label": "Do you have family income information if the provider asks for it?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "deadline", "label": "Have you checked the provider\u2019s current instructions and deadline?", "type": "choice", "options": {"yes": "Yes", "no": "Not yet", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "education", "label": "Education or enrollment information", "question": "education"},
                {"key": "income", "label": "Income information if applicable", "question": "income"},
                {"key": "deadline", "label": "Provider instructions and deadline", "question": "deadline"},
            ],
            "journey": ["Prepare information", "Complete provider application", "Upload or submit supporting details", "Review or verification", "Outcome", "Renewal or follow-up if applicable"],
        },
        "Bank KYC": {
            "category": "Banking",
            "description": "Prepare identity and address information for a bank KYC or re-KYC interaction.",
            "questions": [
                {"key": "identity", "label": "Do you have an accepted identity document ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have current address information or proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "contact", "label": "Can you access the contact details registered with the bank?", "type": "choice", "options": {"yes": "Yes", "no": "Not currently", "unknown": "I need to verify"}},
                {"key": "renewal", "label": "Is this a re-KYC or profile update?", "type": "choice", "options": {"yes": "Yes", "no": "No, first setup", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity document", "question": "identity"},
                {"key": "address", "label": "Current address information", "question": "address"},
                {"key": "contact", "label": "Registered contact access", "question": "contact"},
                {"key": "bank", "label": "Bank-specific KYC instructions", "status": "verify"},
            ],
            "journey": ["Prepare information", "Submit through the bank\u2019s channel", "Bank verification", "Profile update or processing", "Confirmation", "Re-KYC or future update if applicable"],
        },
        "Learner's Licence": {
            "category": "Transport",
            "description": "Prepare for a learner licence journey while leaving local rules to official verification.",
            "questions": [
                {"key": "vehicle", "label": "What vehicle category are you applying for?", "type": "text", "placeholder": "Enter the category if you know it"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have current address proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "rules", "label": "Have you checked the current authority instructions and test requirements?", "type": "choice", "options": {"yes": "Yes", "no": "Not yet", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "address", "label": "Address proof", "question": "address"},
                {"key": "rules", "label": "Current instructions and test requirements", "question": "rules"},
                {"key": "authority", "label": "Authority-specific eligibility and fees", "status": "verify"},
            ],
            "journey": ["Prepare information", "Submit learner licence application", "Verification or appointment", "Learner test if applicable", "Learner licence outcome", "Follow official next-stage instructions"],
        },
        "Driving Licence": {
            "category": "Transport",
            "description": "Map the driving licence journey from preparation through testing and outcome.",
            "questions": [
                {"key": "vehicle", "label": "What vehicle category are you applying for?", "type": "text", "placeholder": "Enter the category if you know it"},
                {"key": "identity", "label": "Do you have identity proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "address", "label": "Do you have current address proof ready?", "type": "choice", "options": {"yes": "Yes, ready", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "learner", "label": "Have you completed any required learner stage?", "type": "choice", "options": {"yes": "Yes", "no": "Not yet", "unknown": "I need to verify"}},
                {"key": "test", "label": "Have you checked the current driving test instructions?", "type": "choice", "options": {"yes": "Yes", "no": "Not yet", "unknown": "I need to verify"}},
            ],
            "checklist": [
                {"key": "identity", "label": "Identity proof", "question": "identity"},
                {"key": "address", "label": "Address proof", "question": "address"},
                {"key": "learner", "label": "Required learner stage", "question": "learner"},
                {"key": "test", "label": "Current driving test instructions", "question": "test"},
            ],
            "journey": ["Prepare information", "Complete any required learner stage", "Submit driving licence application", "Driving test or verification", "Licence outcome", "Renewal or future update if applicable"],
        },
    }
