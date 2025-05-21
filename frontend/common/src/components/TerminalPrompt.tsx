import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card';
import { useClientConfigStore } from '../store/clientConfigStore';

interface TerminalPromptOption {
  value: string;
  label: string;
}

interface TerminalPromptProps {
  text: string;
  options: TerminalPromptOption[];
  onResponse: (response: string) => void;
  onClose: () => void;
}

export const TerminalPrompt: React.FC<TerminalPromptProps> = ({
  text,
  options,
  onResponse,
  onClose
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleResponse = async (value: string) => {
    setIsLoading(true);
    
    try {
      await onResponse(value);
    } finally {
      setIsLoading(false);
      onClose();
    }
  };
  
  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Terminal Prompt</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm font-mono whitespace-pre-wrap">{text}</p>
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
        {options.map((option) => (
          <Button
            key={option.value}
            onClick={() => handleResponse(option.value)}
            disabled={isLoading}
            variant={option.value === 'n' ? 'outline' : 'default'}
          >
            {option.label}
          </Button>
        ))}
      </CardFooter>
    </Card>
  );
};

interface TerminalPromptModalProps {
  isOpen: boolean;
  prompt: {
    text: string;
    options: TerminalPromptOption[];
  } | null;
  onResponse: (response: string) => void;
  onClose: () => void;
}

export const TerminalPromptModal: React.FC<TerminalPromptModalProps> = ({
  isOpen,
  prompt,
  onResponse,
  onClose
}) => {
  if (!isOpen || !prompt) {
    return null;
  }
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <TerminalPrompt
        text={prompt.text}
        options={prompt.options}
        onResponse={onResponse}
        onClose={onClose}
      />
    </div>
  );
};

export const useTerminalPrompt = () => {
  const { host, port } = useClientConfigStore();
  
  const sendResponse = async (response: string) => {
    try {
      const result = await fetch(`http://${host}:${port}/v1/terminal/prompt/response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          response
        })
      });
      
      if (!result.ok) {
        throw new Error(`Failed to send response: ${result.statusText}`);
      }
      
      return true;
    } catch (error) {
      console.error('Error sending terminal prompt response:', error);
      return false;
    }
  };
  
  return { sendResponse };
};
