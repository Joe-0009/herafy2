document.addEventListener('DOMContentLoaded', function () {
    const skillForm = document.getElementById('skill-form');
    const skillsList = document.getElementById('skills-list');
    const noSkillsMessage = document.getElementById('no-skills');

    skillForm.addEventListener('submit', function (event) {
        event.preventDefault();
        
        const formData = new FormData(skillForm);
        const skillName = formData.get('skill');

        // Basic front-end validation
        if (!skillName) {
            console.log('Please enter a skill.');
            return;
        }

        fetch(skillForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  const newSkill = document.createElement('li');
                  newSkill.textContent = skillName;
                  skillsList.appendChild(newSkill);

                  // Remove 'No skills provided' message if it exists
                  if (noSkillsMessage) {
                      noSkillsMessage.remove();
                  }

                  // Clear the form input
                  skillForm.reset();
              } else {
                  console.log(data.message);
              }
          })
          .catch(error => {
              console.error('Error:', error);
          });
    });
});
