function startFeedback() {
    // Navigates to the route defined in main.py
    window.location.href = "/select-category";
}

function goTo(pageName) {
    if (!pageName) return;
    // Uses the dynamic route: /feedback/studentfeedback etc.
    window.location.href = "/feedback/" + pageName;
}

function submit(){
    window.location.href = "/submitted-feedback";
}