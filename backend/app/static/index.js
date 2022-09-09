
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZW5qYW1pbiIsImV4cCI6MTY2MjcyNDU3Mn0.kFYEGeOQPX5X4V9BFlvdKbYBLgtgBtwFBNP8fB1aV8w"
const viewAllIndexes = async () => {

    const res = await fetch("/index", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${access_token}`
        }
      })

    let indexes = await res.json()

    indexes = formatTimeStamps(indexes);

    document.body.appendChild(buildHtmlTable(indexes));

}

const formatTimeStamps = (arr) => {
    return arr.forEach((e) => {
        e['time_created'] = new Date(e['time_created'] * 1000)
        e['time_updated'] = new Date(e['time_updated'] * 1000)
    })
}

const getLogsByPattern = async () => {

    const indexPattern = prompt("Enter Index to search")

    const res = await fetch(`/index/${index}`, {
        method: "POST",
        body: { "index_pattern": indexPattern },
        headers: {
            "Authorization": `Bearer ${access_token}`
        }
      })

    let logs = await res.json()

    logs = formatTimeStamps(logs)

    document.body.appendChild(buildHtmlTable(logs));

}

const getIndexData = async () => {

    const index = prompt("Enter Index to search")

    const res = await fetch(`/index/${index}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${access_token}`
        }
      })

    let logs = await res.json()

    logs = formatTimeStamps(logs)

    document.body.appendChild(buildHtmlTable(logs));

}



const logIn = async () => {
    const username = prompt("Enter Username: ")
    const password = prompt("Enter Password")

    let formData = new FormData()
    formData.append("username", username)
    formData.append("password", password)

    const res = await fetch("/token", {
        method: "POST",
        body: formData
      })

    const body = await res.json()

    console.log(body)

    access_token = body.access_token

    return username;
      

}

const start = async () => {
    username = await logIn()
    document.getElementById('username').innerHTML = `Welcome ${username}`
}

var _table_ = document.createElement('table'),
  _tr_ = document.createElement('tr'),
  _th_ = document.createElement('th'),
  _td_ = document.createElement('td');

  _table_.setAttribute("id", "display-table")

// Builds the HTML Table out of myList json data from Ivy restful service.
function buildHtmlTable(arr) {


if (document.getElementById("display-table")) document.getElementById("display-table").outerHTML = "";
  var table = _table_.cloneNode(false),
    columns = addAllColumnHeaders(arr, table);
  for (var i = 0, maxi = arr.length; i < maxi; ++i) {
    var tr = _tr_.cloneNode(false);
    for (var j = 0, maxj = columns.length; j < maxj; ++j) {
      var td = _td_.cloneNode(false);
      var cellValue = arr[i][columns[j]];
      td.appendChild(document.createTextNode(arr[i][columns[j]] || ''));
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
  return table;
}

// Adds a header row to the table and returns the set of columns.
// Need to do union of keys from all records as some records may not contain
// all records
function addAllColumnHeaders(arr, table) {
  var columnSet = [],
    tr = _tr_.cloneNode(false);
  for (var i = 0, l = arr.length; i < l; i++) {
    for (var key in arr[i]) {
      if (arr[i].hasOwnProperty(key) && columnSet.indexOf(key) === -1) {
        columnSet.push(key);
        var th = _th_.cloneNode(false);
        th.appendChild(document.createTextNode(key));
        tr.appendChild(th);
      }
    }
  }
  table.appendChild(tr);
  return columnSet;
}


document.getElementById("all-indexes").addEventListener('click', viewAllIndexes)
document.getElementById("index-search").addEventListener('click', getIndexData)
document.getElementById("index-pattern-search").addEventListener('click', getLogsByPattern)



 window.onload = start()