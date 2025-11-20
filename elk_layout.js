const elkjs = require('elkjs');
const fs = require('fs');
const path = require('path');

const inputFile = process.argv[2];
const outputFile = inputFile.replace('.json', '_out.json');

if (!inputFile) {
    console.error('❌ Uso: node elk_layout.js <input.json>');
    process.exit(1);
}

// Leer grafo de entrada
let graph;
try {
    graph = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
} catch (err) {
    console.error('❌ Error leyendo archivo:', err.message);
    process.exit(1);
}

// Crear instancia ELK
const elk = new elkjs.default();

// Calcular layout
elk.layout(graph)
    .then(layoutedGraph => {
        // Escribir resultado
        fs.writeFileSync(outputFile, JSON.stringify(layoutedGraph, null, 2));
        console.log('✅ Layout calculado por ELK');
        console.log(`📁 Resultado guardado en: ${outputFile}`);
    })
    .catch(err => {
        console.error('❌ Error en ELK:', err.message);
        process.exit(1);
    });

