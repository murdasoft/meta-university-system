/** Клиентская фильтрация (логика как в Django views). */
window.JobPortalFilters = (function () {
  function postedDt(job) {
    var p = job.posted;
    if (!p) return new Date(0);
    var m = p.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
    if (!m) return new Date(0);
    return new Date(+m[3], +m[2] - 1, +m[1]);
  }

  function formatMatches(jobFormat, want) {
    if (!want) return true;
    var f = (jobFormat || '').toLowerCase();
    if (want === 'remote') return f.indexOf('удал') !== -1;
    if (want === 'hybrid') return f.indexOf('гибрид') !== -1;
    if (want === 'office') return f.indexOf('удал') === -1 && f.indexOf('гибрид') === -1;
    return true;
  }

  function employmentMatches(employment, want) {
    if (!want) return true;
    var e = (employment || '').toLowerCase();
    if (want === 'full') return e.indexOf('полная') !== -1 || (e.indexOf('полн') !== -1 && e.indexOf('част') === -1);
    if (want === 'part') return e.indexOf('частич') !== -1 || e.indexOf('неполн') !== -1 || e.indexOf(' / част') !== -1;
    if (want === 'shift') return e.indexOf('смен') !== -1;
    if (want === 'project') return e.indexOf('проект') !== -1;
    return true;
  }

  function filterVacancies(vacancies, q, city, cat, fmt, emp) {
    q = (q || '').trim().toLowerCase();
    city = (city || '').trim().toLowerCase();
    cat = (cat || '').trim().toLowerCase();
    fmt = (fmt || '').trim().toLowerCase();
    emp = (emp || '').trim().toLowerCase();
    return vacancies.filter(function (j) {
      if (cat && (j.category || '').toLowerCase() !== cat) return false;
      if (city && (j.city || '').toLowerCase().indexOf(city) === -1) return false;
      if (!formatMatches(j.format, fmt)) return false;
      if (!employmentMatches(j.employment, emp)) return false;
      if (q) {
        var blob = [
          j.title,
          j.company,
          j.city,
          j.cat_label || '',
          j.description || '',
          (j.tags || []).join(' '),
        ]
          .join(' ')
          .toLowerCase();
        if (blob.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function sortByPostedDesc(list) {
    return list.slice().sort(function (a, b) {
      return postedDt(b) - postedDt(a);
    });
  }

  function categoryRows(categoryMeta, vacancies) {
    var counts = {};
    vacancies.forEach(function (v) {
      var c = v.category;
      counts[c] = (counts[c] || 0) + 1;
    });
    return Object.keys(categoryMeta)
      .map(function (key) {
        return {
          key: key,
          label: categoryMeta[key].label,
          color: categoryMeta[key].color,
          count: counts[key] || 0,
        };
      })
      .sort(function (a, b) {
        return a.label.localeCompare(b.label, 'ru');
      });
  }

  function uniqueCities(vacancies) {
    var s = {};
    vacancies.forEach(function (v) {
      if (v.city) s[v.city] = true;
    });
    return Object.keys(s).sort(function (a, b) {
      if (a === 'Удалённо') return -1;
      if (b === 'Удалённо') return 1;
        return a.localeCompare(b, 'ru');
    });
  }

  return {
    filterVacancies: filterVacancies,
    sortByPostedDesc: sortByPostedDesc,
    categoryRows: categoryRows,
    uniqueCities: uniqueCities,
    postedDt: postedDt,
  };
})();
