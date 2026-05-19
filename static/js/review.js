/* global google */

function calcDuration(startVal, endVal) {
    if (!startVal || !endVal) return '—';
    const [sh, sm] = startVal.split(':').map(Number);
    const [eh, em] = endVal.split(':').map(Number);
    const mins = (eh * 60 + em) - (sh * 60 + sm);
    if (mins <= 0) return '—';
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return h && m ? `${h}h ${m}m` : h ? `${h}h` : `${m}m`;
}

function updateRowDuration(row) {
    const start = row.querySelector('input[name^="start_time_"]');
    const end = row.querySelector('input[name^="end_time_"]');
    const cell = row.querySelector('td.duration');
    if (start && end && cell) cell.textContent = calcDuration(start.value, end.value);
}

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

function applyBulkColor(colorValue) {
    document.querySelectorAll('input[name^="color_id_"]').forEach(input => {
        input.value = colorValue;
    });
    document.querySelectorAll('#event-rows .color-picker').forEach(picker => {
        picker.querySelectorAll('.swatch').forEach(s => {
            s.classList.toggle('active', s.dataset.color === colorValue);
        });
    });
}

document.querySelectorAll('#event-rows tr').forEach(row => {
    updateRowDuration(row);
    row.querySelectorAll('input[name^="start_time_"], input[name^="end_time_"]').forEach(input => {
        input.addEventListener('change', () => updateRowDuration(row));
    });
});

document.querySelectorAll('#event-rows .color-picker').forEach(picker => {
    picker.querySelectorAll('.swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            picker.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            const input = picker.parentNode.querySelector('input[type="hidden"]');
            if (input) input.value = swatch.dataset.color;
            // Individual change — clear bulk picker's active state
            const bulkPicker = document.getElementById('bulk-color-picker');
            if (bulkPicker) bulkPicker.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
        });
    });
});

const bulkPicker = document.getElementById('bulk-color-picker');
if (bulkPicker) {
    bulkPicker.querySelectorAll('.swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            bulkPicker.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            applyBulkColor(swatch.dataset.color);
        });
    });
}

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
