async function submitEntries(element) {
    element.disabled = true;
    let rows = document.getElementsByClassName("entry");
    const entries = [];
    for (let row of rows) {
        const entry = {
            business_name:row.children[0].innerHTML,
            transaction_date:row.children[1].innerHTML,
            parsedItem:row.children[2].getElementsByTagName("input")[0].defaultValue,
            correctedItem:row.children[2].getElementsByTagName("input")[0].value,
            parsedPrice:row.children[3].getElementsByTagName("input")[0].defaultValue,
            correctedPrice:row.children[3].getElementsByTagName("input")[0].value,
        };
        entries.push(entry);
    }
    const submitBody = JSON.stringify(entries);
    ///*
    // kudos to https://stackoverflow.com/a/38982661
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState != 4) return;

        if (this.status == 200) {
            //var data = JSON.parse(this.responseText);

            // we get the returned data
            alert(this.responseText);
        }
        else {
            alert(this.statusText);
        }
        element.disabled = false;

        // end of state change: it can be after some time (async)
    };
    xhr.open("PUT", document.getElementById("app").href, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    //xhr.setRequestHeader('Content-Disposition', 'inline');
    xhr.send(submitBody);
    //*/
    /*
    const response = await fetch(document.getElementById("app").href, {
        method: 'PUT',
        headers: {
            'Content-type': 'application/json',
            //'Content-Disposition': 'inline',
        },
        body: submitBody
    });
      
    // Awaiting response.json() 
    //const responseData = await response.json();
    if (response.ok) {
        const responseData = await response.text();
        alert(responseData);
    }
    else {
        alert(response.statusText);
    }
    element.disabled = false;
    */
}
function deleteEntry(element) {
    let row = element.parentElement.parentElement;
    row.remove();
}

