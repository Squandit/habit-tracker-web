const habitList = document.querySelector('#habit-list');

async function loadHabits() {
  const response = await fetch('/api/habits-list');
  const data = await response.json();

  habitList.replaceChildren();

  for (const habit of data.habits) {
    const article = document.createElement('article');
    article.className = 'habit-card';

    const name = document.createElement('h3');
    name.className = 'habit-name';
    name.textContent = habit.name.charAt(0).toUpperCase() + habit.name.slice(1);

    const description = document.createElement('p');
    description.className = 'habit-description';
    description.textContent = habit.description || 'No description';

    article.append(name, description);
    habitList.append(article);
  }
}

loadHabits();
