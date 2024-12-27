import fs from 'fs';
import path from 'path';

interface Route {
  route: string;
  headers?: Record<string, string>;
  rewrite?: string;
  allowedRoles?: string[];
}

interface StaticWebAppConfig {
  routes: Route[];
  navigationFallback?: {
    rewrite: string;
    exclude?: string[];
  };
  globalHeaders?: Record<string, string>;
  mimeTypes?: Record<string, string>;
}

function isWildcardRoute(route: string): boolean {
  return route.includes('*');
}

function isRouteMatchedByWildcard(route: string, wildcardRoute: string): boolean {
  if (!isWildcardRoute(wildcardRoute)) return false;
  
  const wildcardParts = wildcardRoute.split('/');
  
  // Remove the last part with * from wildcard
  const wildcardPrefix = wildcardParts.slice(0, -1).join('/');
  
  // Check if the route starts with the wildcard prefix
  return route.startsWith(wildcardPrefix);
}

function findConflictingRoutes(routes: Route[]): { route: string; conflictingWildcards: string[] }[] {
  const conflicts: { route: string; conflictingWildcards: string[] }[] = [];
  
  for (let i = 0; i < routes.length; i++) {
    const currentRoute = routes[i].route;
    if (isWildcardRoute(currentRoute)) continue;
    
    const conflictingWildcards = routes
      .slice(0, i)
      .filter(r => isWildcardRoute(r.route) && isRouteMatchedByWildcard(currentRoute, r.route))
      .map(r => r.route);
    
    if (conflictingWildcards.length > 0) {
      conflicts.push({
        route: currentRoute,
        conflictingWildcards
      });
    }
  }
  
  return conflicts;
}

describe('Static Web App Configuration Validation', () => {
  let config: StaticWebAppConfig;
  
  beforeAll(() => {
    const configPath = path.join(__dirname, '../../staticwebapp.config.json');
    const configContent = fs.readFileSync(configPath, 'utf-8');
    config = JSON.parse(configContent);
  });
  
  test('configuration file exists and is valid JSON', () => {
    expect(config).toBeDefined();
    expect(config.routes).toBeDefined();
  });
  
  test('no routes are covered by wildcard routes', () => {
    const conflicts = findConflictingRoutes(config.routes);
    
    if (conflicts.length > 0) {
      const errorMessages = conflicts.map(
        ({ route, conflictingWildcards }) =>
          `Route "${route}" is covered by wildcard route(s): ${conflictingWildcards.join(', ')}`
      );
      
      throw new Error(
        'Found route conflicts:\n' +
        errorMessages.join('\n') +
        '\n\nFix by either:\n' +
        '1. Removing the covered routes\n' +
        '2. Moving specific routes before wildcard routes\n' +
        '3. Making wildcard routes more specific'
      );
    }
  });
  
  test('all routes have required properties', () => {
    config.routes.forEach(route => {
      expect(route.route).toBeDefined();
      expect(typeof route.route).toBe('string');
    });

    // Test optional properties only when they exist
    const routesWithHeaders = config.routes.filter(r => r.headers);
    routesWithHeaders.forEach(route => {
      expect(typeof route.headers).toBe('object');
    });

    const routesWithRewrite = config.routes.filter(r => r.rewrite);
    routesWithRewrite.forEach(route => {
      expect(typeof route.rewrite).toBe('string');
    });

    const routesWithRoles = config.routes.filter(r => r.allowedRoles);
    routesWithRoles.forEach(route => {
      expect(Array.isArray(route.allowedRoles)).toBe(true);
    });
  });
  
  test('MIME types are properly configured', () => {
    expect(config.mimeTypes).toBeDefined();
    const mimeTypes = config.mimeTypes as Record<string, string>;
    
    const requiredMimeTypes = ['.js', '.css', '.json'];
    requiredMimeTypes.forEach(ext => {
      expect(mimeTypes[ext]).toBeDefined();
    });
  });
}); 