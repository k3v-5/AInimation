export interface MigrationStep {
  fromVersion: string;
  toVersion: string;
  description: string;
}

export interface MigrationPlan {
  sourceVersion: string;
  targetVersion: string;
  steps: MigrationStep[];
  canMigrate: boolean;
}

export interface Migration {
  fromVersion: string;
  toVersion: string;
  description: string;
  canMigrate(projectData: any): boolean;
  migrate(projectData: any): any;
}
