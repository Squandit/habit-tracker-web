const habitList = document.querySelector('#habit-list');
async function loadHabits() {
  const response = await fetch('/api/habits-list');
  const data = await response.json();
  habitList.replaceChildren();

  for (const habit of data.habits) {
    const article = document.createElement('label');
    article.className = 'habit-card';

    const name = document.createElement('h3');
    name.className = 'habit-name';
    name.textContent = habit.name.charAt(0).toUpperCase() + habit.name.slice(1);

    const description = document.createElement('p');
    description.className = 'habit-description';
    description.textContent = habit.description || 'No description';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'habit-checkbox'
    checkbox.dataset.habitId = habit.id;
    checkbox.checked = habit.done_today;

    checkbox.addEventListener('change', async () => {
  if (checkbox.checked) {
    anime({
      targets: article,
      scale: [1, 1.05, 1],
      duration: 300,
      easing: 'easeInOutQuad'
    });
    confetti({
      particleCount: 60,
      spread: 55,
      origin: { x: 0.5, y: 0.5 }
    });
  }
  if (!checkbox.checked) {
    await fetch('/api/log-habit', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: checkbox.dataset.habitId })
    });
    return;
  }
  await fetch('/api/log-habit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: checkbox.dataset.habitId })
  });
});
    article.append(name, description, checkbox);
    habitList.append(article);
  }
}

const newHabitName = document.querySelector('#new-habit-name-input');
const newHabitDescription = document.querySelector('#new-habit-description-input');

const addHabitConfirmButton = document.querySelector('#add-habit-confirm');
addHabitConfirmButton.addEventListener('click', createHabit);

async function createHabit() {
  await fetch('/api/add-habit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newHabitName.value, description: newHabitDescription.value })
  });
}

const addHabitButton = document.querySelector('#add-habit');
const exitPopupButton = document.querySelector('#exit-popup');
const modalOverlay = document.querySelector('.modal-overlay');

addHabitButton.addEventListener('click', () => {
  newHabitName.value = '';
  newHabitDescription.value = '';
  modalOverlay.classList.remove('hidden');
  anime({
    targets: '.new-habit-popup-box',
    translateY: ['100%', '0%'],
    duration: 350,
    easing: 'easeOutCubic'
  });
});

exitPopupButton.addEventListener('click', () => {
  anime({
    targets: '.new-habit-popup-box',
    translateY: ['0%', '100%'],
    duration: 250,
    easing: 'easeInCubic',
    complete: () => modalOverlay.classList.add('hidden')
  });
  loadHabits();
});

addHabitConfirmButton.addEventListener('click', async () => {
  await createHabit();
  loadHabits();
  modalOverlay.classList.add('hidden')
});

loadHabits();