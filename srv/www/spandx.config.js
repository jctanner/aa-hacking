/*global module, process*/
const localhost = (process.env.PLATFORM === 'linux') ? 'localhost' : 'host.docker.internal';

module.exports = {
    routes: {
        '/apps/automation-analytics': { host: `https://aafrontend:8002` },
        '/ansible/automation-analytics': { host: `https://aafrontend:8002` },
        '/beta/ansible/automation-analytics': { host: `https://aafrontend:8002` },
        '/api/tower-analytics': { host: `http://fastapi:8080` },
        '/apps/chrome': { host: `http://webroot` },
        '/apps/landing': { host: `http://webroot` },
        '/beta/apps/landing': { host: `http://webroot` },
        '/api/entitlements': { host: `http://entitlements` },
        '/api/rbac': { host: `http://rbac` },
        '/beta/config': { host: `http://${localhost}:8889` },
        '/': { host: `http://webroot` }
    }
};
