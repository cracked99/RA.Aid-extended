import React, { useState, useEffect } from 'react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetClose
} from './ui/sheet';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useClientConfigStore } from '../store/clientConfigStore';
import { fetchSettings, updateSettings } from '../utils/api';

// Define model info interface
interface ModelInfo {
  id: string;
  name: string;
  description: string;
  context_length: number;
  supports_temperature: boolean;
  default_temperature: number;
  is_free: boolean;
  category: string;
}

// Define settings interface
interface ModelSettings {
  provider: string;
  model: string;
  temperature: number | null;
  expert_enabled: boolean;
  web_research_enabled: boolean;
}

// Define settings response interface
interface SettingsResponse {
  settings: ModelSettings;
  available_providers: string[];
  available_models: {
    [provider: string]: ModelInfo[];
  };
}

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose
}) => {
  // Get client config
  const { host, port } = useClientConfigStore();

  // State for settings
  const [settings, setSettings] = useState<ModelSettings>({
    provider: 'anthropic',
    model: 'claude-3-7-sonnet-20250219',
    temperature: 0.7,
    expert_enabled: true,
    web_research_enabled: false
  });

  // State for Tavily API key availability
  const [isTavilyAvailable, setIsTavilyAvailable] = useState<boolean>(false);

  // State for available options
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [availableModels, setAvailableModels] = useState<{[provider: string]: ModelInfo[]}>({});

  // State for loading
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  // Fetch settings when modal opens
  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen, host, port]);

  // Load settings from API
  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchSettings({ host, port });

      if (response) {
        setSettings(response.settings);
        setAvailableProviders(response.available_providers);
        setAvailableModels(response.available_models);

        // Check if Tavily API key is available
        // We'll assume it's available if web_research_enabled is true in the response
        // since the backend will disable it if the key is not available
        setIsTavilyAvailable(response.settings.web_research_enabled);
      }
    } catch (err) {
      setError('Failed to load settings. Please try again.');
      console.error('Error loading settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Save settings
  const saveSettings = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await updateSettings({ host, port, settings });
      setSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err) {
      setError('Failed to save settings. Please try again.');
      console.error('Error saving settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle provider change
  const handleProviderChange = (value: string) => {
    // Update provider and reset model
    const newSettings = {
      ...settings,
      provider: value,
      model: availableModels[value]?.[0]?.id || '',
      // Keep expert mode setting
      expert_enabled: settings.expert_enabled
    };

    setSettings(newSettings);
  };

  // Handle model change
  const handleModelChange = (value: string) => {
    // Find model info
    const modelInfo = availableModels[settings.provider]?.find(m => m.id === value);

    // Update model and temperature if needed
    const newSettings = {
      ...settings,
      model: value,
      temperature: modelInfo?.supports_temperature ? modelInfo.default_temperature : null
    };

    setSettings(newSettings);
  };

  // Get current model info
  const getCurrentModelInfo = (): ModelInfo | undefined => {
    return availableModels[settings.provider]?.find(m => m.id === settings.model);
  };

  // Render model options for current provider
  const renderModelOptions = () => {
    const models = availableModels[settings.provider] || [];

    return models.map(model => (
      <SelectItem key={model.id} value={model.id}>
        {model.name} {model.is_free ? '(Free)' : ''}
      </SelectItem>
    ));
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader className="mb-4">
          <SheetTitle>Model Settings</SheetTitle>
          <SheetDescription>
            Configure the AI model used by RA.Aid
          </SheetDescription>
        </SheetHeader>

        {isLoading ? (
          <div className="flex items-center justify-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                Settings saved successfully!
              </div>
            )}

            {/* Provider Selection */}
            <div className="space-y-2">
              <Label htmlFor="provider">Provider</Label>
              <Select
                value={settings.provider}
                onValueChange={handleProviderChange}
                disabled={isLoading}
              >
                <SelectTrigger id="provider">
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent>
                  {availableProviders.map(provider => (
                    <SelectItem key={provider} value={provider}>
                      {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Model Selection */}
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select
                value={settings.model}
                onValueChange={handleModelChange}
                disabled={isLoading}
              >
                <SelectTrigger id="model">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {renderModelOptions()}
                </SelectContent>
              </Select>

              {/* Model Description */}
              {getCurrentModelInfo()?.description && (
                <p className="text-xs text-muted-foreground mt-1">
                  {getCurrentModelInfo()?.description}
                </p>
              )}

              {/* OpenRouter Warning */}
              {settings.provider === 'openrouter' && (
                <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-2 rounded mt-2 text-xs">
                  <p className="font-semibold">Note about OpenRouter:</p>
                  <p>Even "free" models require credits on OpenRouter. Make sure your account has credits.</p>
                  <p className="mt-1">
                    <a
                      href="https://openrouter.ai/settings/credits"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline"
                    >
                      Add credits to your OpenRouter account
                    </a>
                  </p>
                </div>
              )}
            </div>

            {/* Temperature Setting */}
            {getCurrentModelInfo()?.supports_temperature && (
              <div className="space-y-2">
                <Label htmlFor="temperature">
                  Temperature ({settings.temperature})
                </Label>
                <Input
                  id="temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature || 0.7}
                  onChange={(e) => setSettings({
                    ...settings,
                    temperature: parseFloat(e.target.value)
                  })}
                  disabled={isLoading}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>More Deterministic</span>
                  <span>More Creative</span>
                </div>
              </div>
            )}

            {/* Expert Mode Toggle */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="expert-mode" className="block">Expert Mode</Label>
                <p className="text-xs text-muted-foreground">
                  Enable expert mode for more detailed responses
                </p>
              </div>
              <Switch
                id="expert-mode"
                checked={settings.expert_enabled}
                onCheckedChange={(checked) => setSettings({
                  ...settings,
                  expert_enabled: checked
                })}
                disabled={isLoading}
              />
            </div>

            {/* Web Research Toggle */}
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="web-research" className="block">Web Research</Label>
                <p className="text-xs text-muted-foreground">
                  {isTavilyAvailable
                    ? "Enable web research for up-to-date information"
                    : "Web research requires Tavily API key (TAVILY_API_KEY)"}
                </p>
              </div>
              <Switch
                id="web-research"
                checked={settings.web_research_enabled && isTavilyAvailable}
                onCheckedChange={(checked) => setSettings({
                  ...settings,
                  web_research_enabled: checked
                })}
                disabled={isLoading || !isTavilyAvailable}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-2 pt-4">
              <SheetClose asChild>
                <Button variant="outline" disabled={isLoading}>
                  Cancel
                </Button>
              </SheetClose>
              <Button onClick={saveSettings} disabled={isLoading}>
                {isLoading ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
};
