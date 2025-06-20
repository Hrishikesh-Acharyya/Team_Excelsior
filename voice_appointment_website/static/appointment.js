async function validateAndUpdateSlot(structuredData)
{
  try{
    console.log(structuredData.datetime);
    const response = await fetch(`${HOST_NAME}/voice_data_extraction/validate-slot/`,{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(structuredData),
    });

    const slot_result = await response.json();

     if (slot_result.error) {
            consoleDiv.innerHTML += `<p>[❌] ${slot_result.error}</p>`;
            return;
        }

    const doctorName = slot_result.doctor;
    const specialization = slot_result.specialization;
    const slot = slot_result.slot;
    
    
    // Parse slot date/time
    const [dateStr, timeStr] = slot.split(' ');

    if(slot) dateField.value = dateStr;
    if(slot) timeField.value = timeStr;

    updateBookingField('doctor', doctorName);
    updateBookingField('specialization', specialization);
    updateBookingField('date', dateStr);
    updateBookingField('time', timeStr);

    consoleField.innerHTML = `<p>[📅] Appointment booking with ${slot_result.doctor} on ${dateStr} at ${timeStr}</p>`;

  }catch (err) {
        consoleField.innerHTML += `<p>[❌] Could not validate preferred time slot.</p>`;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const doctorSelect = document.getElementById('doctor');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time');

    async function updateTimeSlots() {
        const doctorId = doctorSelect.value;
        const date = dateInput.value;

        // Clear old options
        timeSelect.innerHTML = "";

        if (!date) return;

        if (!doctorId) {
            // Show all default slots if no doctor is selected
            const defaultTimes = generateDefaultTimeSlots();
            populateTimeOptions(defaultTimes);
            return;
        }

        // Doctor is selected, fetch available slots
        try {
            const response = await fetch(`${HOST_NAME}/voice_data_extraction/available_slots/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ doctorId: doctorId, date: date })
            });

            if (!response.ok) throw new Error("Failed to fetch slots");

            const data = await response.json();
            const availableTimes = data.available_slots; // assumed format: ["10:00", "10:15", ...]
            populateTimeOptions(availableTimes);
        } catch (error) {
            console.error("Error fetching time slots:", error);
        }
    }

    function generateDefaultTimeSlots() {
    const slots = [];
    const now = new Date();
    const selectedDate = new Date(dateInput.value);
    const isToday = now.toDateString() === selectedDate.toDateString();

    const startHour = 8;
    const endHour = 23;
    const intervalMinutes = 15;

    for (let hour = startHour; hour <= endHour; hour++) {
        for (let min = 0; min < 60; min += intervalMinutes) {
            if (hour === endHour && min > 15) break;

            const slot = new Date(selectedDate);
            slot.setHours(hour, min, 0, 0);

            if (!isToday || slot > now) {
                const timeStr = `${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
                slots.push(timeStr);
            }
        }
    }

    return slots;
}
    function populateTimeOptions(slots) {
        slots.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            timeSelect.appendChild(option);
        });
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Attach listeners
    doctorSelect.addEventListener('change', updateTimeSlots);
    dateInput.addEventListener('change', updateTimeSlots);
});

document.getElementById('submit-button').addEventListener('click', async function () {
    const formData = {
        doctorId: document.getElementById('doctor').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        name: document.getElementById('name').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        symptoms: document.getElementById('symptoms').value,
    };

    try {
        const response = await fetch(`${HOST_NAME}/create_appointment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();
        if (response.ok) {
            alert("✅ Appointment booked successfully!");
            window.location.href = "/";  // redirect to index
        } else {
            alert("❌ " + (result.error || "Failed to book appointment"));
        }
    } catch (err) {
        console.error("Submission failed:", err);
        alert("❌ Error occurred while booking appointment.");
    }
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
