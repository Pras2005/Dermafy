function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

const questions = [
    { question: "What is your primary skin concern?", options: ["Acne", "Dryness", "Oily skin", "Sensitivity"] },
    { question: "What is your skin type?", options: ["Oily", "Dry", "Combination", "Normal"] },
    { question: "How often do you experience breakouts?", options: ["Rarely", "Occasionally", "Frequently", "Severe"] },
    { question: "How does your skin react to new skincare products?", options: ["No reaction", "Mild redness", "Irritation", "Severe reaction"] },
    { question: "Do you experience redness or inflammation?", options: ["No", "Sometimes", "Frequently", "Persistent redness"] },
    { question: "How often do you apply sunscreen?", options: ["Daily", "Only when outside", "Sometimes", "Never"] },
    { question: "Do you have any skin conditions?", options: ["Eczema", "Psoriasis", "Rosacea", "None"] },
    { question: "How does your skin feel after washing?", options: ["Comfortable", "Tight", "Oily", "Irritated"] },
    { question: "How much water do you drink daily?", options: ["Less than 1L", "1-2L", "More than 2L", "I don't track"] },
    { question: "Do you have dark spots or pigmentation?", options: ["No", "Light spots", "Visible spots", "Severe pigmentation"] }
];

let currentQuestionIndex = 0;
let userResponses = [];
let selectedOption = null;

const questionEl = document.getElementById("question");
const optionsEl = document.getElementById("options");
const nextBtn = document.getElementById("next-btn");
const progressBar = document.getElementById("progress-bar");

function startQuiz() {
    currentQuestionIndex = 0;
    userResponses = [];
    selectedOption = null;
    nextBtn.disabled = true;
    showQuestion();
}

function showQuestion() {
    resetState();
    const currentQuestion = questions[currentQuestionIndex];
    questionEl.textContent = currentQuestion.question;

    currentQuestion.options.forEach(option => {
        const button = document.createElement("button");
        button.classList.add("option");
        button.textContent = option;
        button.addEventListener("click", () => selectAnswer(button, option));
        optionsEl.appendChild(button);
    });

    updateProgressBar();
}

function resetState() {
    optionsEl.innerHTML = "";
    nextBtn.disabled = true;
    selectedOption = null;
}

function selectAnswer(button, option) {
    document.querySelectorAll(".option").forEach(btn => btn.classList.remove("selected"));
    button.classList.add("selected");
    selectedOption = option;
    nextBtn.disabled = false;
}

function nextQuestion() {
    if (selectedOption === null) return;
    
    userResponses.push(selectedOption);
    
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        showQuestion();
    } else {
        questionEl.textContent = "Quiz Completed! Thank you for your response.";
        //optionsEl.innerHTML = `<p>Your results :</p><ul>${userResponses.map(response => `<li>${response}</li>`).join('')}</ul>`;
        progressBar.style.width = "100%";

        const dashboardBtn = document.createElement("button");
        dashboardBtn.textContent = "GO TO DASHBOARD";
        dashboardBtn.classList.add("btn", "dashboard-btn");
        dashboardBtn.addEventListener("click", () => {
            window.location.href = "/dashboard/";
        });
        optionsEl.appendChild(dashboardBtn);

        nextBtn.style.display = "none";
    }
}

function updateProgressBar() {
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;
}

nextBtn.addEventListener("click", nextQuestion);

startQuiz();
