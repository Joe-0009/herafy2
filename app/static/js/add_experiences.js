document.addEventListener('DOMContentLoaded', function () {
    const experienceForm = document.getElementById('experience-form');
    const experiencesList = document.getElementById('experiences-list');
    const noExperiencesMessage = document.getElementById('no-experiences');

    if (experienceForm) {
        experienceForm.addEventListener('submit', function (event) {
            event.preventDefault();
            
            const formData = new FormData(experienceForm);
            const experienceTitle = formData.get('experience');
            const company = formData.get('company');
            const startDate = formData.get('start_date');
            const endDate = formData.get('end_date');
            const description = formData.get('description');

            // Basic front-end validation
            if (!experienceTitle || !company || !startDate || !endDate) {
                console.log('Please complete all required fields.');
                return;
            }

            fetch(experienceForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            }).then(response => response.json())
              .then(data => {
                  if (data.success) {
                      const newExperience = document.createElement('li');
                      newExperience.textContent = `${experienceTitle} at ${company} (${startDate} to ${endDate})`;
                      experiencesList.appendChild(newExperience);

                      // Remove 'No experience provided' message if it exists
                      if (noExperiencesMessage) {
                          noExperiencesMessage.remove();
                      }

                      // Clear the form input
                      experienceForm.reset();
                  } else {
                      console.log(data.message);
                  }
              })
              .catch(error => {
                  console.error('Error:', error);
              });
        });
    }
});
