// home.js
const searchInput = document.getElementById('searchInput');
const suggestionsContainer = document.getElementById('suggestions');
const checkAvailabilityButton = document.getElementById('checkAvailabilityButton');
const statusMessage = document.getElementById('statusMessage');
let selectedSiteId = null;

searchInput.addEventListener('input', async () => {
    const query = searchInput.value.trim();
    if (!query) {
        suggestionsContainer.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/api/autocomplete-sites/?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            suggestionsContainer.innerHTML = data.results
                .map(site => `
                    <div class="autocomplete-suggestion" onclick="selectSuggestion(${site.id}, '${site.nazwa}')">
                        ${site.nazwa} - ${site.ulica || ''} (${site.kod_pocztowy || ''})
                    </div>
                `).join('');
        } else {
            suggestionsContainer.innerHTML = '<div class="autocomplete-suggestion">Brak wyników</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        suggestionsContainer.innerHTML = '<div class="autocomplete-suggestion">Błąd serwera</div>';
    }
});

function selectSuggestion(id, nazwa) {
    selectedSiteId = id;
    searchInput.value = `${nazwa}`;
    suggestionsContainer.innerHTML = '';
}

checkAvailabilityButton.addEventListener('click', async () => {
    if (!selectedSiteId) {
        alert('Wybierz parking z listy!');
        return;
    }

    try {
        const response = await fetch(`/api/available-parking-spots-for-site/${selectedSiteId}/`);
        const data = await response.json();

        if (data.available_spots >= 0) {
            statusMessage.textContent = `Dostępne miejsca: ${data.available_spots}`;
        } else {
            statusMessage.textContent = 'Wystąpił błąd. Spróbuj ponownie.';
        }
    } catch (error) {
        console.error('Error:', error);
        statusMessage.textContent = 'Błąd serwera. Spróbuj ponownie.';
    }
});
