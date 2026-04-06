/** Редирект на login при отсутствии сессии или несовпадении роли. */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var need = document.body.getAttribute('data-require-role');
    if (!need) return;
    var u = window.JobPortalShell && JobPortalShell.getUser();
    if (!u) {
      window.location.href = 'login.html';
      return;
    }
    if (u.role !== need) {
      var map = {
        seeker: 'seeker-dashboard.html',
        employer: 'employer-dashboard.html',
        admin: 'admin-users.html',
      };
      var t = map[u.role];
      window.location.href = t || 'index.html';
    }
  });
})();
