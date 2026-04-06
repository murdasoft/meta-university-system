(function () {
  function esc(s) {
    if (s == null) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var D = window.JOB_PORTAL_DATA;
    var slug = (window.location.hash || '').replace(/^#/, '').trim();
    var root = document.getElementById('vacancy-root');
    var empty = document.getElementById('vacancy-empty');
    if (!D || !root) return;
    if (!slug) {
      root.style.display = 'none';
      if (empty) empty.style.display = 'block';
      return;
    }
    var job = (D.vacancies || []).find(function (j) {
      return j.slug === slug;
    });
    if (!job) {
      root.style.display = 'none';
      if (empty) {
        empty.style.display = 'block';
        empty.innerHTML =
          '<p class="mock-empty">Вакансия не найдена. <a href="vacancies.html">К каталогу</a></p>';
      }
      return;
    }
    if (empty) empty.style.display = 'none';
    document.title = job.title + ' — Портал вакансий';

    root.innerHTML =
      '<div class="mock-detail__badge" style="--card-accent: ' +
      esc(job.accent_color) +
      ';">' +
      esc(job.cat_label) +
      '</div>' +
      '<h1 class="mock-page-title">' +
      esc(job.title) +
      '</h1>' +
      '<p class="mock-detail__company">' +
      esc(job.company) +
      '</p>' +
      '<ul class="mock-detail__facts">' +
      '<li><strong>Локация и формат:</strong> ' +
      esc(job.city) +
      ' · ' +
      esc(job.format) +
      '</li>' +
      '<li><strong>Занятость:</strong> ' +
      esc(job.employment) +
      '</li>' +
      '<li><strong>Оплата:</strong> ' +
      esc(job.salary) +
      '</li>' +
      '<li><strong>Опубликовано:</strong> ' +
      esc(job.posted) +
      '</li></ul>' +
      '<div class="mock-detail__tags">' +
      (job.tags || [])
        .map(function (t) {
          return '<span class="mock-tag">' + esc(t) + '</span>';
        })
        .join('') +
      '</div>' +
      '<h2 class="mock-section-title mock-section-title--decor" style="margin-top:1.5rem;">Описание</h2>' +
      '<p class="mock-detail__body">' +
      esc(job.description) +
      '</p>' +
      '<div class="mock-detail__actions">' +
      '<span class="mock-btn mock-btn--primary" role="button" tabindex="0">Откликнуться</span>' +
      '<span class="mock-btn" role="button" tabindex="0">Сохранить</span></div>';

    window.onhashchange = function () {
      window.location.reload();
    };
  });
})();
