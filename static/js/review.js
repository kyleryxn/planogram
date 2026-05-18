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

document.querySelectorAll('.color-picker').forEach(picker => {
    picker.querySelectorAll('.swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            picker.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            const input = picker.parentNode.querySelector('input[type="hidden"]');
            if (input) input.value = swatch.dataset.color;
        });
    });
});

async function initAutocomplete() {
    const { AutocompleteSuggestion } = await google.maps.importLibrary('places');

    document.querySelectorAll('input[name^="location_"]').forEach(input => {
        const datalist = document.createElement('datalist');
        datalist.id = `dl-${input.name}`;
        input.setAttribute('list', datalist.id);
        input.parentNode.appendChild(datalist);

        let debounce;
        input.addEventListener('input', function () {
            clearTimeout(debounce);
            datalist.innerHTML = '';
            if (input.value.length < 2) return;
            debounce = setTimeout(async () => {
                try {
                    const { suggestions } = await AutocompleteSuggestion.fetchAutocompleteSuggestions({
                        input: input.value,
                    });
                    datalist.innerHTML = suggestions.slice(0, 5).map(s =>
                        `<option value="${s.placePrediction.text.text}"></option>`
                    ).join('');
                } catch (e) {
                    console.error('autocomplete error:', e);
                }
            }, 300);
        });
    });
}
