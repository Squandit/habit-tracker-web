const habitList = document.querySelector('#habit-list');
const addHabitButton = document.querySelector('#add-habit-btn');

async function loadHabits() {
	try {
		const response = await fetch('/api/habits-list');

		if (!response.ok) {
			throw new Error(`Request failed: ${response.status}`);
		}

		const data = await response.json();
		habitList.replaceChildren();

		if (data.habits.length === 0) {
			habitList.textContent = 'No habits yet.';
			return;
		}

		for (const habit of data.habits) {
			const habitElement = document.createElement('article');
			const name = document.createElement('h2');
			const description = document.createElement('p');

			name.textContent = habit.name;
			description.textContent = habit.description || 'No description';
			habitElement.append(name, description);
			habitList.append(habitElement);
		}
	} catch (error) {
		habitList.textContent = 'Could not load habits.';
		console.error(error);
	}
}

function addHabit() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}

loadHabits();