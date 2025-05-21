/**
 * API utilities for making requests to the RA.Aid server
 */

import { useClientConfigStore } from '../store/clientConfigStore';

/**
 * Interface for spawn agent request parameters
 */
export interface SpawnAgentParams {
  /**
   * Message content to send
   */
  message: string;

  /**
   * Whether to use research-only mode
   */
  research_only?: boolean;

  /**
   * Whether to reset the workspace before starting the agent
   */
  reset_workspace?: boolean;
}

/**
 * Interface for spawn agent response
 */
export interface SpawnAgentResponse {
  /**
   * ID of the created session
   */
  session_id: string;

  /**
   * Status message
   */
  status: string;
}

/**
 * Error class for API errors
 */
export class ApiError extends Error {
  /**
   * HTTP status code
   */
  statusCode: number;

  /**
   * Response object
   */
  response: Response;

  constructor(message: string, statusCode: number, response: Response) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.response = response;
  }
}

/**
 * Makes a request to spawn a new agent with the given message
 *
 * @param params - Request parameters
 * @returns Promise with the spawn agent response
 * @throws ApiError if the request fails
 */
export async function spawnAgent(params: SpawnAgentParams): Promise<SpawnAgentResponse> {
  const { host, port } = useClientConfigStore.getState();

  try {
    const response = await fetch(`http://${host}:${port}/v1/spawn-agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: params.message,
        research_only: params.research_only || false,
        reset_workspace: params.reset_workspace || false
      })
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to spawn agent: ${response.statusText}`,
        response.status,
        response
      );
    }

    const data = await response.json();
    return data as SpawnAgentResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new Error(
      error instanceof Error
        ? `Failed to spawn agent: ${error.message}`
        : 'Failed to spawn agent: Unknown error'
    );
  }
}

/**
 * Interface for model information
 */
export interface ModelInfo {
  /**
   * Model ID
   */
  id: string;

  /**
   * Display name
   */
  name: string;

  /**
   * Model description
   */
  description: string;

  /**
   * Context length in tokens
   */
  context_length: number;

  /**
   * Whether the model supports temperature
   */
  supports_temperature: boolean;

  /**
   * Default temperature value
   */
  default_temperature: number;

  /**
   * Whether the model is free to use
   */
  is_free: boolean;

  /**
   * Model category (e.g., coding, general)
   */
  category: string;
}

/**
 * Interface for model settings
 */
export interface ModelSettings {
  /**
   * Provider name
   */
  provider: string;

  /**
   * Model name
   */
  model: string;

  /**
   * Temperature value
   */
  temperature: number | null;

  /**
   * Whether expert mode is enabled
   */
  expert_enabled: boolean;

  /**
   * Whether web research is enabled
   */
  web_research_enabled: boolean;
}

/**
 * Interface for settings response
 */
export interface SettingsResponse {
  /**
   * Current model settings
   */
  settings: ModelSettings;

  /**
   * List of available providers
   */
  available_providers: string[];

  /**
   * Available models by provider
   */
  available_models: {
    [provider: string]: ModelInfo[];
  };
}

/**
 * Interface for fetch settings parameters
 */
export interface FetchSettingsParams {
  /**
   * Server host
   */
  host: string;

  /**
   * Server port
   */
  port: number;
}

/**
 * Interface for update settings parameters
 */
export interface UpdateSettingsParams {
  /**
   * Server host
   */
  host: string;

  /**
   * Server port
   */
  port: number;

  /**
   * Settings to update
   */
  settings: ModelSettings;
}

/**
 * Fetches the current settings from the server
 *
 * @param params - Request parameters
 * @returns Promise with the settings response
 * @throws ApiError if the request fails
 */
export async function fetchSettings(params: FetchSettingsParams): Promise<SettingsResponse> {
  try {
    const response = await fetch(`http://${params.host}:${params.port}/v1/settings`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to fetch settings: ${response.statusText}`,
        response.status,
        response
      );
    }

    const data = await response.json();
    return data as SettingsResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new Error(
      error instanceof Error
        ? `Failed to fetch settings: ${error.message}`
        : 'Failed to fetch settings: Unknown error'
    );
  }
}

/**
 * Updates the settings on the server
 *
 * @param params - Request parameters
 * @returns Promise with the updated settings
 * @throws ApiError if the request fails
 */
export async function updateSettings(params: UpdateSettingsParams): Promise<ModelSettings> {
  try {
    const response = await fetch(`http://${params.host}:${params.port}/v1/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params.settings)
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to update settings: ${response.statusText}`,
        response.status,
        response
      );
    }

    const data = await response.json();
    return data as ModelSettings;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new Error(
      error instanceof Error
        ? `Failed to update settings: ${error.message}`
        : 'Failed to update settings: Unknown error'
    );
  }
}