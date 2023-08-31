% import os
% fzf_js = os.path.join(template_base_dir, 'fzf.umd.js.tpl')
<script>
    % include(fzf_js)
</script>

<script>
    % if file_details_json:
        const fileDetailsList = {{!file_details_json}};
    % else:
        const fileDetailsList = [];
    % end

    const fuzzySearch = new fzf.Fzf(fileDetailsList, {
        selector: (item) => item.fileName
    });

    // Loading elements into memory
    const dataRowsParent = document.getElementsByClassName("file-list")[0];
    const dataRows = dataRowsParent.getElementsByClassName("data-row");
    const fragment = document.createDocumentFragment();
    const originalElements = new Map();
    for (let i = 0; i < dataRows.length; i++) {
        const element = dataRows[i];
        const id = element.getAttribute("id");
        originalElements.set(id, element);
    }

    function removeAllRows() {
        const rows = dataRowsParent.getElementsByClassName("data-row");
        for(let i = rows.length - 1; i >= 0; i--) {
            const row = rows[i];
            row.parentNode.removeChild(row);
        }
    }

    function clearSearch() {
        removeAllRows();
        for (const [id, element] of originalElements) {
            fragment.appendChild(element);
        }
        dataRowsParent.appendChild(fragment);
    }

    const searchField = document.getElementById("search")
    const clearIcon = document.getElementById("clearInput");
    clearIcon.addEventListener("click", function() {
        searchField.value = "";
        clearSearch();
        clearIcon.style.display = "none";
    });

    function handleSearch(searchQuery) {
        clearIcon.style.display = searchQuery.length ? "block" : "none";
            if (!searchQuery) {
                clearSearch();
                return false;
            }
            let matches = fuzzySearch.find(searchQuery);
            for (const match of matches) {
                const obj = match.item;
                const hash = obj.hash;
                const element = originalElements.get(hash);
                fragment.appendChild(element);
            }
            removeAllRows();
            dataRowsParent.appendChild(fragment);
    }

    function registerSearch(input) {
        input.addEventListener("input", function(e) {
            let searchQuery = this.value;
            handleSearch(searchQuery);
        });
    }
    registerSearch(searchField);

    window.addEventListener("pageshow", () => {
      // To back button search field pre-fill.
      const searchFieldValue = searchField.value;
      if (!searchFieldValue) {
        return;
      }
      handleSearch(searchFieldValue);
    });

</script>

<style>
    div.autocomplete-wrapper {
        padding-bottom: 15px;
    }
    div.autocomplete {
        width: 40%;
        position: relative;
        display: inline-block;

        display: inline-block;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #ffffff;
        padding-bottom: 8px;
    }
    div.autocomplete input#search {
        width: 98%;

        padding-top: 4px;
        padding-bottom: 4px;
        border: none;
        border-radius: 4px;
        box-shadow: none;
        font-size: 14px;

    }

    div.autocomplete input#search:focus {
        outline: none;
        box-shadow: 0px 0px 6px rgba(0, 0, 0, 0.1);
    }

    .clear-icon {
      position: absolute;
      top: 50%;
      right: 10px;
      transform: translateY(-50%);
      cursor: pointer;
      display: none;
      color: red;
    }
</style>