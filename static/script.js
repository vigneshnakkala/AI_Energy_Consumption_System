function showLoad(msg){
    console.log(msg);
}

function hideLoad(){
    console.log("done");
}

function toast(msg){
    alert(msg);
}

function showPage(id){
    document.querySelectorAll('.pg').forEach(p => p.style.display = 'none');
    document.getElementById(id).style.display = 'block';
}// ======================
// GLOBAL NAVIGATION
// ======================
function goTo(pageNumber){
    document.querySelectorAll("[id^='page']").forEach(p => p.style.display = "none");
    document.getElementById("page" + pageNumber).style.display = "block";
}

// ======================
// TOAST MESSAGE
// ======================
function showToast(msg){
    alert(msg);
}

// ======================
// STEP 1: SEND OTP (REAL BACKEND)
// ======================
function sendOTP(){

    const name = document.getElementById("name").value;
    const gender = document.getElementById("gender").value;
    const email = document.getElementById("email").value;

    if(!name || !gender || !email){
        showToast("⚠️ Fill all fields");
        return;
    }

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `name=${encodeURIComponent(name)}&gender=${encodeURIComponent(gender)}&email=${encodeURIComponent(email)}`
    })
    .then(res => {
        console.log("LOGIN RESPONSE:", res);

        if(res.redirected){
            showToast("📨 OTP sent to your email");
            goTo(4); // go to OTP page
        } else {
            showToast("❌ Failed to send OTP");
        }
    })
    .catch(err => {
        console.log(err);
        showToast("❌ Server error");
    });
}

// ======================
// STEP 2: VERIFY OTP
// ======================
function verifyOTP(){

    const entered = ['d1','d2','d3','d4','d5','d6']
        .map(id => document.getElementById(id).value)
        .join('');

    if(entered.length < 6){
        showToast("⚠️ Enter full OTP");
        return;
    }

    fetch("/verify_otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `otp=${entered}`
    })
    .then(res => {
        console.log("VERIFY RESPONSE:", res);

        if(res.redirected){
            showToast("✅ OTP Verified");

            // 🔥 REDIRECT TO BACKEND PAGE
            window.location.href = res.url;

        } else {
            showToast("❌ Invalid OTP");
        }
    })
    .catch(err => {
        console.log(err);
        showToast("❌ Server error");
    });
}
// ======================
// STEP 3: PREDICTION
// ======================
function runPrediction(){

    const temp = document.getElementById("temp").value;
    const hum = document.getElementById("hum").value;
    const wind = document.getElementById("wind").value;
    const solar = document.getElementById("solar").value;
    const peak = document.getElementById("peak").value;

    // 🔥 VALIDATION FIX
    if(!temp || !hum || !wind || !solar || !peak){
        showToast("⚠️ Fill all fields");
        return;
    }

    fetch("/prediction", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            temperature: parseFloat(temp),
            humidity: parseFloat(hum),
            wind_speed: parseFloat(wind),
            solar_radiation: parseFloat(solar),
            peak_hour_indicator: parseFloat(peak)
        })
    })
    .then(res => res.json())
    .then(data => {

        console.log("PREDICTION DATA:", data);

        if(data.error){
            showToast("❌ Prediction failed");
            return;
        }

        document.getElementById("result").innerHTML =
            `⚡ Energy: ${data.prediction} kWh <br> 💰 Cost: ₹${data.cost}`;

        // 🔥 ALERT SOUND FIX
        if(data.status === "⚠️ Very High Usage" || data.status === "Very High Usage"){
            alert("⚠️ HIGH ENERGY ALERT!");

            let audio = new Audio("https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg");
            audio.play().catch(() => console.log("Sound blocked by browser"));
        }
    })
    .catch(err => {
        console.log(err);
        showToast("❌ Server error");
    });
}