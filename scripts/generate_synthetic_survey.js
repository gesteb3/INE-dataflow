const fs = require('node:fs');
const path = require('node:path');

const totalRows = 10000;
const headers = [
  'record_id',
  'survey_code',
  'interview_date',
  'department_code',
  'municipality_code',
  'urban_rural',
  'respondent_age',
  'respondent_sex',
  'household_size',
  'monthly_income_gtq',
];

const sexValues = ['F', 'M', 'X', 'NR'];
const rows = [headers.join(',')];

for (let index = 1; index <= totalRows; index += 1) {
  const department = String(((index - 1) % 22) + 1).padStart(2, '0');
  const municipality = String(((index - 1) % 99) + 1).padStart(2, '0');
  const day = String(((index - 1) % 20) + 1).padStart(2, '0');
  const age = 18 + ((index * 7) % 73);
  const householdSize = 1 + ((index * 3) % 8);
  const income = (900 + ((index * 137) % 7600)).toFixed(2);

  rows.push([
    `HOGAR-${String(index).padStart(6, '0')}`,
    'ENHOGAR',
    `2026-08-${day}`,
    department,
    `${department}${municipality}`,
    index % 3 === 0 ? 'R' : 'U',
    age,
    sexValues[(index - 1) % sexValues.length],
    householdSize,
    income,
  ].join(','));
}

const outputPath = path.resolve(__dirname, '..', 'data', 'samples', 'encuesta_10000.csv');
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${rows.join('\n')}\n`, 'utf8');
console.log(`Archivo generado: ${outputPath}`);
console.log(`Registros generados: ${totalRows}`);
