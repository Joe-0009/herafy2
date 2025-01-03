document.addEventListener('DOMContentLoaded', function () {
    // Toggle the Add Skill form
    const addSkillLink = document.getElementById('add-skill-link');
    const addSkillForm = document.getElementById('add-skill-form');

    if (addSkillLink) {
        addSkillLink.addEventListener('click', function (event) {
            event.preventDefault();
            addSkillForm.style.display = (addSkillForm.style.display === 'none' || addSkillForm.style.display === '') ? 'block' : 'none';
        });
    }

    // Toggle the Add Experience form
    const addExperienceLink = document.getElementById('add-experience-link');
    const addExperienceForm = document.getElementById('add-experience-form');

    if (addExperienceLink) {
        addExperienceLink.addEventListener('click', function (event) {
            event.preventDefault();
            addExperienceForm.style.display = (addExperienceForm.style.display === 'none' || addExperienceForm.style.display === '') ? 'block' : 'none';
        });
    }
});
