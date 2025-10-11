// Paste this in the Script field of Custom HTML Block.
// NOTE: Custom HTML Block injects a variable named root_element.
(function(){
  try {
    if (!root_element) return;
    const widget = root_element.querySelector('.balance-widget');
    if (!widget) return;

    const tbody = widget.querySelector('tbody');
    const metaEl = widget.querySelector('.bw-meta');
    const company = widget.getAttribute('data-company') || '';
    const account = widget.getAttribute('data-account') || '';

    const fmt = new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 4 });

    function renderRows(rows){
      tbody.innerHTML = '';
      if(!rows || !rows.length){
        tbody.innerHTML = '<tr><td colspan="2" class="empty">No data</td></tr>';
        return;
      }
      rows.forEach(function(r){
        var tr = document.createElement('tr');

        var acc = Array.isArray(r) ? r[0] : (r.account || '-');
        var bal = Array.isArray(r) ? r[1] : (r.balance || 0);
        var val = Number(bal || 0);

        // First cell: Account (left)
        var tdAcc = document.createElement('td');
        tdAcc.textContent = acc || '-';

        // Second cell: Balance (left, colored by sign)
        var tdBal = document.createElement('td');
        tdBal.textContent = fmt.format(val);
        if (val < 0) {
          tdBal.style.color = '#dc2626';
        } else if (val > 0) {
          tdBal.style.color = '#059669';
        } else {
          tdBal.style.color = '';
        }

        tr.appendChild(tdAcc);
        tr.appendChild(tdBal);
        tbody.appendChild(tr);
      });
    }

    async function fetchFromReport(){
      var payload = {
        report_name: 'balance',
        filters: Object.assign({}, company ? { company: company } : {}, account ? { account: account } : {})
      };

      if (window.frappe && typeof frappe.call === 'function') {
        try {
          var res = await frappe.call({ method: 'frappe.desk.query_report.run', args: payload });
          var rows = (res && res.message && res.message.result) || [];
          renderRows(rows);
          if (company) metaEl.textContent = 'Company: ' + company;
          return true;
        } catch (e) {}

        try {
          var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
          if (frappe && frappe.csrf_token) headers['X-Frappe-CSRF-Token'] = frappe.csrf_token;
          var resp = await fetch('/api/method/frappe.desk.query_report.run', {
            method: 'POST', headers: headers, body: JSON.stringify(payload), credentials: 'same-origin',
          });
          var json = await resp.json();
          var rows2 = (json && json.message && json.message.result) || [];
          renderRows(rows2);
          if (company) metaEl.textContent = 'Company: ' + company;
          return true;
        } catch (e2) {}
      }
      return false;
    }

    if (window.balanceData) {
      renderRows(window.balanceData);
    } else {
      fetchFromReport().then(function(ok){
        if(!ok){
          renderRows([
            { account: 'Cash - Main', balance: 12345.6789 },
            { account: 'Bank - USD', balance: -250.5 },
          ]);
        }
      });
    }
  } catch (err) {
    // swallow errors in block
  }
})();
