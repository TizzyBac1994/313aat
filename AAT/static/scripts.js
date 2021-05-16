const questionFormContainers = document.getElementsByClassName("assessment-question");

for (const container of questionFormContainers) {
  const mcqForm = container.getElementsByClassName("answer-mcq-question")[0];
  const ftbForm = container.getElementsByClassName("answer-ftb-question")[0];
  const ansDisplay = container.querySelector(".selected-answer");
  if (ansDisplay) {
    container.classList.add("answered");
  } else {
    container.classList.add("not-answered");
  }
  if (mcqForm) {
    mcqForm.addEventListener('formdata', e => {
      const selectedRadioLabel = mcqForm.querySelector("input[type='radio'][name='answer']:checked + label");
      const ansString = selectedRadioLabel.textContent;
      if (ansDisplay) {
        ansDisplay.querySelector("strong").textContent = ansString;
      } else {
        const newAnsDisplay = document.createElement("p");
        newAnsDisplay.className = "selected-answer";
        newAnsDisplay.innerHTML = `Submitted answer: <strong>${ansString}</strong>`;
        container.appendChild(newAnsDisplay);
        container.classList.remove("not-answered");
        container.classList.add("answered");
      }
    })
  }
  if (ftbForm) {
    ftbForm.addEventListener('formdata', e => {
      e.preventDefault();
      let data = e.formData;
      let answers = [];
      for (const val of data) {
        if (val[0].startsWith("answer")) {
          answers.push(val[1]);
        }
      }
      const ansString = answers.join(", ");
      if (ansDisplay) {
        ansDisplay.querySelector("strong").textContent = ansString;
      } else {
        const newAnsDisplay = document.createElement("p");
        newAnsDisplay.className = "selected-answer";
        newAnsDisplay.innerHTML = `Submitted answer: <strong>${ansString}</strong>`;
        container.appendChild(newAnsDisplay);
        container.classList.remove("not-answered");
        container.classList.add("answered");
      }
    });
  }
}

const submissionsContainers = document.getElementsByClassName("submissions-container");

for (const subsContainer of submissionsContainers) {
  const showBtn = subsContainer.querySelector(".show-submissions-btn");

  if (showBtn) {
    showBtn.addEventListener('click', e => {
      const subsList = subsContainer.querySelector(".submissions-list");
      if (subsList.classList.contains("hidden")) {
        showBtn.textContent = "Hide submissions";
        subsList.classList.remove("hidden");
      } else {
        showBtn.textContent = "Show submissions";
        subsList.classList.add("hidden");
      }
    })
  }
}

const hintContainers = document.getElementsByClassName("question-hint");

for (const hintCont of hintContainers) {
  const showBtn = hintCont.querySelector(".hint-btn");
  if (showBtn) {
    showBtn.addEventListener('click', e => {
      const hintText = hintCont.querySelector(".hint-text")
      if (hintText.classList.contains("show")) {
        hintText.classList.remove("show");
        showBtn.textContent = "Show hint"
      } else {
        hintText.classList.add("show");
        showBtn.textContent = "Hint:"
        showBtn.setAttribute('disabled', '');
      }
    })
  }
}