// Grabs the container all habit cards get added into. Queried once,
// reused every time loadHabits() re-renders the list.
const habitList = document.querySelector('#habit-list');

async function loadHabits() {
  // Fetches every habit from the server, including whether each one
  // has already been marked done today (done_today).
  const response = await fetch('/api/habits-list');
  const data = await response.json();

  // Clears out whatever's currently in #habit-list (the "Loading
  // habits..." message, or last render's cards) before adding the
  // fresh set.
  habitList.replaceChildren();

  for (const habit of data.habits) {
    // <label> instead of <article> so clicking anywhere on the card
    // (not just the checkbox itself) toggles the checkbox, since a
    // checkbox nested inside a <label> does that automatically.
    const article = document.createElement('label');
    article.className = 'habit-card';

    const name = document.createElement('h3');
    name.className = 'habit-name';
    // Capitalizes just the first letter for display (doesn't change
    // what's stored in the database).
    name.textContent = habit.name.charAt(0).toUpperCase() + habit.name.slice(1);

    const description = document.createElement('p');
    description.className = 'habit-description';
    description.textContent = habit.description || 'No description';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'habit-checkbox'
    // Tags the checkbox with which habit it belongs to, so the change
    // listener below knows what to send to the server.
    checkbox.dataset.habitId = habit
    checkbox.checked = habit.done_today;



    // TODO: checkbox.checked is never set above, so every checkbox
    // starts unchecked on page load even if habit.done_today is true.
    // Should be: checkbox.checked = habit.done_today;

    // Fires whenever the checkbox is ticked or unticked by an actual
    // click (setting .checked from code does NOT fire this).
    checkbox.addEventListener('change', async () => {
  // Little pulse animation on the card itself, then a confetti burst.
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

  // Tells the server this habit is done today. Doesn't currently
  // handle unchecking separately, so ticking it again after a reload
  // would send another log-habit request for the same day.
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




loadHabits();