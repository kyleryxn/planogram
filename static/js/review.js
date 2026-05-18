/* global google */

function deleteRow(btn) {
    btn.closest('tr').remove();
    const tbody = document.getElementById('event-rows');
    Array.from(tbody.rows).forEach((row, i) => {
        row.cells[0].textContent = String(i + 1);
        row.querySelectorAll('input[name]').forEach(input => {
            input.name = input.name.replace(/_\d+$/, '_' + i);
        });
    });
}

function applyBulkName(value) {
    document.querySelectorAll('input[name^="title_"]').forEach(input => {
        input.value = value;
    });
}

async function initAutocomplete() {
    const { PlaceAutocompleteElement } = await google.maps.importLibrary('places');
    document.querySelectorAll('input[name^="location_"]').forEach(input => {
        const pac = new PlaceAutocompleteElement();
        pac.id = `pac-${input.name}`;
        input.parentNode.insertBefore(pac, input);
        input.style.display = 'none';
        pac.addEventListener('gmp-placeselect', ({ place }) => {
            input.value = place.displayName || place.formattedAddress || '';
        });
    });
}
