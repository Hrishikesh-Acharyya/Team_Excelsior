const fieldMap = {
    name: 'summary-name',
    age: 'summary-age',
    gender: 'summary-gender',
    phone: 'summary-phone',
    email: 'summary-email',
    symptoms: 'summary-symptoms',
    doctor: 'summary-doctor',
    date: 'summary-date',
    time: 'summary-time',
  };


function displayStructuredData(structuredData) {
    if (!nameField.readOnly && structuredData.name !== null && structuredData.name !== undefined) nameField.value = structuredData.name;
    if (structuredData.age !== null && structuredData.age !== undefined) ageField.value = structuredData.age;
    if (structuredData.gender !== null && structuredData.gender !== undefined) genderField.value = structuredData.gender;
    if (!nameField.readOnly && structuredData.phone !== null && structuredData.phone !== undefined) phoneField.value = structuredData.phone;
    if (structuredData.symptoms !== null && structuredData.symptoms !== undefined) symptomsField.value = structuredData.symptoms;
    if (structuredData.email !== null && structuredData.email !== undefined) emailField.value = structuredData.email;
    if (structuredData.doctor !== null && structuredData.doctor !== undefined) doctorField.value = structuredData.doctor;
    if (structuredData.datetime !== null && structuredData.datetime !== undefined) {
    // Split ISO string into date and time
    const [datePart, timePart] = structuredData.datetime.split('T');
    if (datePart) dateField.value = datePart;
    if (timePart) timeField.value = timePart.slice(0,5); // "14:00:00" -> "14:00"
}

  updateBookingField('name', nameField.value);
  updateBookingField('age', ageField.value);
  updateBookingField('gender', genderField.value);
  updateBookingField('phone', phoneField.value);
  updateBookingField('email', emailField.value);
  updateBookingField('symptoms', symptomsField.value);
  updateBookingField('doctor', doctorField.value);
  updateBookingField('date', dateField.value);
  updateBookingField('time', timeField.value);

}

document.addEventListener("DOMContentLoaded", () => {
    if (isLoggedIn) {
        // Disable fields that should come from user info
        nameField.readOnly = true;
        phoneField.readOnly = true;

        updateBookingField('name', nameField.value);
        updateBookingField('phone', phoneField.value);
    }
});


  

  // Update booking summary line for a field
  function updateBookingField(field, value) {
    const output = document.getElementById(fieldMap[field]);
    const input = document.getElementById(field);
    if (output) {
      output.textContent = value?.trim() || (['doctor', 'date', 'time'].includes(field) ? 'Not selected' : 'Not filled');
    }
    if (input) {
      input.value = value;
    }
  }

  // Hook up live updates for typing or selection
  Object.keys(fieldMap).forEach(field => {
    const input = document.getElementById(field);
    if (input) {
      input.addEventListener('input', () => {
        updateBookingField(field, input.value);
      });
    }
  });
