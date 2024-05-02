// const baseUrl = 'https://resumematchpro-dev-function-app.azurewebsites.net/api/files';
const baseUrl = 'http://localhost:7071/api/files';

export const uploadFiles = async (files: File[], userId: string, type: string) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('content', file);
  });
  formData.append('user_id', userId);
  formData.append('type', type);

  const response = await fetch(`${baseUrl}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('File upload failed');
  }

  return response.json();
};

export const getFiles = async (userId: string, type: string) => {
  const response = await fetch(`${baseUrl}?user_id=${userId}&type=${type}`);

  if (!response.ok) {
    throw new Error('Failed to get files');
  }

  return response.json();
};
