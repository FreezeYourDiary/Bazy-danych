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

// wybiera proponowa
function selectSuggestion(id, nazwa) {
    selectedSiteId = id;
    searchInput.value = `${nazwa}`;
    suggestionsContainer.innerHTML = '';
}

checkAvailabilityButton.addEventListener('click', async () => {
    statusMessage.style.display = 'block';

    if (!selectedSiteId) {
        alert('Wybierz parking z listy!');
        statusMessage.style.display = 'none';  // hide message
        return;
    }

    // transfer polskie znaki na backend api
    const filterMapping = {
        'dla pracowników': 'pracownikow',
        'dla samochodów ciężarowych': 'ciezarowych',
        'podziemny': 'podziemny',
    };

    const selectedFilters = Array.from(document.querySelectorAll('.filterCheckbox:checked'))
        .map(cb => filterMapping[cb.value] || cb.value);

    try {
        const filterParams = selectedFilters.map(filter => `filters=${encodeURIComponent(filter)}`).join('&');
        const url = `/api/available-parking-spots-with-filters/${selectedSiteId}/?${filterParams}`;

        const response = await fetch(url);
        const data = await response.json();

        if (response.ok && data.available_spots >= 0) {
            statusMessage.textContent = `Dostępne miejsca: ${data.available_spots}`;

            if (data.prices && Object.keys(data.prices).length > 0) {
                let priceDetails = "<h4>Cennik:</h4><ul>";
                const parkingNames = ['A', 'B', 'C', 'D', 'E'];

                let index = 0;
                for (let parkingId in data.prices) {
                    const price = data.prices[parkingId];
                    const parkingName = parkingNames[index] || `Strefa ${parkingId}`;
                    priceDetails += `<li>Strefa: ${parkingName} - ${price} zł/godz.</li>`;
                    index++;
                }
                priceDetails += "</ul>";
                statusMessage.innerHTML += priceDetails;
            }
            // prompt redirect na strone rezerwacji
            const reservationPrompt = document.createElement('div');
            reservationPrompt.innerHTML = `
                <p>Chcesz stworzyć rezerwację?</p>
                <button id="confirmReservation" class="button">Tak</button>
                <button id="cancelReservation" class="button">Nie</button>
            `;
            statusMessage.appendChild(reservationPrompt);

            document.getElementById('confirmReservation').addEventListener('click', async () => {
                try {
                    const loginStatusResponse = await fetch('/is_logged_in/');
                    const loginStatusData = await loginStatusResponse.json();

                    if (loginStatusData.logged_in) {
                        window.location.href = `/konto`;
                    } else {
                        alert('Musisz być zalogowany, aby dokonać rezerwacji.');
                        window.location.href = '/login/';
                    }
                } catch (error) {
                    console.error('Error checking login status:', error);
                    alert('Wystąpił błąd podczas sprawdzania stanu logowania. Spróbuj ponownie.');
                }
            });

            document.getElementById('cancelReservation').addEventListener('click', () => {
                statusMessage.innerHTML = ''; // Clear the status message
                statusMessage.style.display = 'none';
            });

        } else {
            statusMessage.textContent = "Brak dostępnych miejsc dla wybranych filtrów.";
        }
    } catch (error) {
        console.error('Error fetching parking availability:', error);
        statusMessage.textContent = "Błąd serwera";
    }

});
