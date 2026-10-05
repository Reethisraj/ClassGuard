console.log("JS LOADED");
const API_URL = "http://127.0.0.1:8000";


/* ================= SCROLL ================= */

function scrollToRequest() {

    document
        .getElementById("requestSection")
        .scrollIntoView({
            behavior: "smooth"
        });
}


/* ================= FORM ================= */

const requestForm =
    document.getElementById("requestForm");

const resultCard =
    document.getElementById("resultCard");

const analyzeBtn =
    document.getElementById("analyzeBtn");


requestForm.addEventListener("submit", async function (event) {

    event.preventDefault();


    /* -------------------------
       GET FORM VALUES
    ------------------------- */

    const userId =
        document.getElementById("userId").value.trim();

    const purpose =
        document.getElementById("purpose").value.trim();

    const date =
        document.getElementById("date").value;

    const startTime =
        document.getElementById("startTime").value;

    const endTime =
        document.getElementById("endTime").value;

    const students =
        document.getElementById("students").value;

    const projector =
        document.getElementById("projector").checked;


    /* -------------------------
       BASIC VALIDATION
    ------------------------- */

    if (startTime >= endTime) {

        showError(
            "End time must be later than start time."
        );

        return;
    }


    /* -------------------------
       LOADING
    ------------------------- */

    analyzeBtn.disabled = true;

    analyzeBtn.textContent =
        "Analyzing...";


    resultCard.innerHTML = `
        <div class="loading">
            ClassGuard is analyzing your request...
        </div>
    `;


    /* -------------------------
       API REQUEST
    ------------------------- */

    try {

        const params = new URLSearchParams({

            user_id: userId,

            date: date,

            start_time: startTime,

            end_time: endTime,

            students: students,

            projector_required: projector,

            purpose: purpose

        });


        const response =
            await fetch(
                `${API_URL}/analyze-request?${params.toString()}`
            );


        if (!response.ok) {

            throw new Error(
                "Backend request failed"
            );
        }


        const data =
            await response.json();


        /* -------------------------
           DISPLAY RESULT
        ------------------------- */

        displayResult(data);


    } catch (error) {

        console.error(error);

        showError(
            "Unable to connect to ClassGuard backend. Make sure the FastAPI server is running."
        );

    } finally {

        analyzeBtn.disabled = false;

        analyzeBtn.textContent =
            "Analyze Request";
    }

});


/* ================= DISPLAY RESULT ================= */

function displayResult(data) {

    if (!data.success) {

        showError(
            data.message || "Request failed."
        );

        return;
    }


    let roomHTML = "";


    if (data.recommended_room) {

        roomHTML = `

            <div class="result-section">

                <h4>
                    Recommended Classroom
                </h4>

                <div class="room-box">

                    <strong>
                        Room ${data.recommended_room.room_id}
                    </strong>

                    <p>
                        Capacity:
                        ${data.recommended_room.capacity}
                    </p>

                    <p>
                        Projector:
                        ${
                            data.recommended_room.projector
                                ? "Available"
                                : "Not Available"
                        }
                    </p>

                </div>

            </div>

        `;
    }


    let policiesHTML = "";


    if (
        data.relevant_policies &&
        data.relevant_policies.length > 0
    ) {

        policiesHTML = `

            <div class="result-section">

                <h4>
                    Retrieved Policies
                </h4>

                ${data.relevant_policies
                    .map(policy => `
                        <div class="policy-item">
                            ${policy}
                        </div>
                    `)
                    .join("")
                }

            </div>

        `;
    }


    resultCard.innerHTML = `

        <div>

            <div class="result-title">
                CLASSGUARD DECISION
            </div>

            <div class="decision">
                ${data.decision}
            </div>


            <div class="result-section">

                <h4>
                    System Reason
                </h4>

                <p>
                    ${data.reason || "No reason provided."}
                </p>

            </div>


            ${roomHTML}


            <div class="result-section">

                <h4>
                    AI Agent Analysis
                </h4>

                <p>
                    ${
                        data.gemini_analysis
                        || "AI analysis unavailable."
                    }
                </p>

            </div>


            ${policiesHTML}

        </div>

    `;
}


/* ================= ERROR ================= */

function showError(message) {

    resultCard.innerHTML = `

        <div class="result-placeholder">

            <div class="result-icon">
                !
            </div>

            <h3>
                Request Error
            </h3>

            <p>
                ${message}
            </p>

        </div>

    `;
}