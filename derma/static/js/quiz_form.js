document.addEventListener("DOMContentLoaded", function () {
    const questions = [
        { name: "primary_skin_concern", question: "What is your primary skin concern?", options: ["Acne", "Dryness", "Oily skin", "Sensitivity"] },
        { name: "skin_type", question: "What is your skin type?", options: ["Oily", "Dry", "Combination", "Normal"] },
        { name: "breakout_frequency", question: "How often do you experience breakouts?", options: ["Rarely", "Occasionally", "Frequently", "Severe"] },
        { name: "reaction_to_skincare", question: "How does your skin react to new skincare products?", options: ["No reaction", "Mild redness", "Irritation", "Severe reaction"] },
        { name: "redness_inflammation", question: "Do you experience redness or inflammation?", options: ["No", "Sometimes", "Frequently", "Persistent redness"] },
        { name: "sunscreen_usage", question: "How often do you apply sunscreen?", options: ["Daily", "Only when outside", "Sometimes", "Never"] },
        { name: "skin_conditions", question: "Do you have any skin conditions?", options: ["Eczema", "Psoriasis", "Rosacea", "None"] },
        { name: "after_washing_skin_feel", question: "How does your skin feel after washing?", options: ["Comfortable", "Tight", "Oily", "Irritated"] },
        { name: "water_intake", question: "How much water do you drink daily?", options: ["Less than 1L", "1-2L", "More than 2L", "I don't track"] },
        { name: "dark_spots_pigmentation", question: "Do you have dark spots or pigmentation?", options: ["No", "Light spots", "Visible spots", "Severe pigmentation"] },
        { name: "visible_pores", question: "Do you have visible pores?", options: ["None", "Few", "Moderate", "Large"] },
        { name: "exfoliation_frequency", question: "How often do you exfoliate?", options: ["Daily", "2-3 times a week", "Once a week", "Rarely"] },
        { name: "fine_lines_wrinkles", question: "Do you have fine lines or wrinkles?", options: ["None", "Light", "Moderate", "Severe"] },
        { name: "dairy_processed_food_intake", question: "How often do you consume dairy or processed foods?", options: ["Daily", "Often", "Rarely", "Never"] },
        { name: "skincare_routine", question: "Do you follow a skincare routine?", options: ["Yes, regularly", "Sometimes", "Rarely", "Never"] }
    ];

    let currentQuestionIndex = 0;
    let userResponses = {};
    let selectedOption = null;

    const questionEl = document.getElementById("question");
    const optionsEl = document.getElementById("options");
    const nextBtn = document.getElementById("next-btn");
    const submitBtn = document.getElementById("submit-btn");
    const progressBar = document.getElementById("progress-bar");
    const quizForm = document.getElementById("quiz-form");

    function showQuestion() {
        resetState();
        const currentQuestion = questions[currentQuestionIndex];

        if (!currentQuestion) {
            console.error("No more questions.");
            return;
        }

        questionEl.textContent = currentQuestion.question;

        currentQuestion.options.forEach(option => {
            const button = document.createElement("button");
            button.classList.add("option");
            button.textContent = option;
            button.setAttribute("type", "button");
            button.addEventListener("click", () => selectAnswer(button, currentQuestion.name, option));
            optionsEl.appendChild(button);
        });

        updateProgressBar();
    }

    function resetState() {
        optionsEl.innerHTML = "";
        nextBtn.style.display = "block";
        submitBtn.style.display = "none";
        selectedOption = null;
        nextBtn.disabled = true;
    }

    function selectAnswer(button, fieldName, option) {
        document.querySelectorAll(".option").forEach(btn => btn.classList.remove("selected"));
        button.classList.add("selected");
        selectedOption = option;
        userResponses[fieldName] = option;
        nextBtn.disabled = false;
    }

    function nextQuestion() {
        if (!selectedOption) return;

        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            showQuestion();
        } else {
            showSubmitButton();
        }
    }

    function showSubmitButton() {
        nextBtn.style.display = "none";
        submitBtn.style.display = "block";

        // Create hidden input fields for all answers
        Object.keys(userResponses).forEach(field => {
            if (!quizForm.querySelector(`input[name="${field}"]`)) {
                const input = document.createElement("input");
                input.type = "hidden";
                input.name = field;
                input.value = userResponses[field];
                quizForm.appendChild(input);
            }
        });
    }

    function updateProgressBar() {
        const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
        progressBar.style.width = `${progress}%`;
    }

    nextBtn.addEventListener("click", nextQuestion);
    showQuestion();
});
