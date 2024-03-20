dfd.readCSV("https://raw.githubusercontent.com/jmajety-lab/data/main/final_dropdown.csv?token=GHSAT0AAAAAACNDVQL3UIBFCQC25T5HDYQOZP2OCPA")
.then(df => {
    const countyColumn = document.getElementById('countyColumn');
    df['COUNTY'].values.forEach(value => {
        const div = document.createElement('div');
        div.textContent = value;
        countyColumn.appendChild(div);
    });
})
.catch(err => {
    console.log(err);
});

const county_dict = {
    'ALLEGANY': 1,
    'ANNE ARUNDEL': 2,
    'BALTIMORE': 3,
    'CALVERT': 4,
    'CAROLINE': 5,
    'CARROLL': 6,
    'CECIL': 7,
    'CHARLES': 8,
    'DORCHESTER': 9,
    'FREDERICK': 10,
    'GARRETT': 11,
    'HARFORD': 12,
    'HOWARD': 13,
    'KENT': 14,
    'MONTGOMERY': 15,
    'PRINCE GEORGES': 16,
    'QUEEN ANNES': 17,
    'ST. MARYS': 18,
    'SOMERSET': 19,
    'TALBOT': 20,
    'WASHINGTON': 21,
    'WICOMICO': 22,
    'WORCESTER': 23,
    'BALTIMORE CITY': 24,
};

function get_county_code(county_name) {
    return county_dict[county_name.toUpperCase()] || null;
}

function read_data(){
    var url = "https://raw.githubusercontent.com/jmajety-lab/data/main/final_dropdown.csv?token=GHSAT0AAAAAACNDVQL3UIBFCQC25T5HDYQOZP2OCPA";
    dfd.readCSV(url)
    return dfd.readCSV(url)
}
function read_crash_data(){
    var url = "https://www.kaggle.com/datasets/jmajety/crash-data";
    dfd.readCSV(url)
    return dfd.readCSV(url)
}