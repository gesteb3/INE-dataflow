import fs from 'node:fs/promises';
import path from 'node:path';

const totalRows = 12000;
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

const outputPath = path.resolve('data', 'samples', 'encuesta_12000_demo_errores.csv');
const sexValues = ['F', 'M', 'X', 'NR'];
const rows = [headers.join(',')];
let intentionalErrorRows = 0;

for (let index = 1; index <= totalRows; index += 1) {
  const department = String(((index - 1) % 22) + 1).padStart(2, '0');
  const municipality = String(((index - 1) % 99) + 1).padStart(2, '0');
  const day = String(((index - 1) % 28) + 1).padStart(2, '0');
  let recordId = `HOGAR-${String(index).padStart(6, '0')}`;
  let surveyCode = 'ENHOGAR';
  let interviewDate = `2026-08-${day}`;
  let urbanRural = index % 3 === 0 ? 'R' : 'U';
  let age = 18 + ((index * 7) % 73);
  let sex = sexValues[(index - 1) % sexValues.length];
  let householdSize = 1 + ((index * 3) % 8);
  let income = (900 + ((index * 137) % 7600)).toFixed(2);

  const hasError = index % 293 === 0 || index % 367 === 0 || index % 419 === 0
    || index % 503 === 0 || index % 641 === 0 || index % 733 === 0
    || index % 887 === 0 || index % 911 === 0 || index % 997 === 0;
  if (hasError) intentionalErrorRows += 1;

  if (index % 293 === 0) surveyCode = '';
  if (index % 367 === 0) recordId = `HOGAR/${String(index).padStart(6, '0')}`;
  if (index % 419 === 0) interviewDate = '2027-01-01';
  if (index % 503 === 0) income = '-25.00';
  if (index % 641 === 0) householdSize = 0;
  if (index % 733 === 0) sex = 'Z';
  if (index % 777 === 0) recordId = 'HOGAR-000001';
  if (index % 887 === 0) age = 135;
  if (index % 911 === 0) urbanRural = 'X';
  if (index % 997 === 0) income = '';
  if (index % 157 === 0) income = ` ${income} `;

  rows.push([
    recordId,
    surveyCode,
    interviewDate,
    department,
    `${department}${municipality}`,
    urbanRural,
    age,
    sex,
    householdSize,
    income,
  ].join(','));
}

const csvText = `\ufeff${rows.join('\n')}\n`;
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, csvText, 'utf8');

console.log(`Archivo generado: ${outputPath}`);
console.log(`Registros generados: ${totalRows}`);
console.log(`Filas con errores intencionales: ${intentionalErrorRows}`);
