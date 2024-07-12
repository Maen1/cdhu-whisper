<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-6">
    <div class="bg-white shadow-md rounded-lg p-8 w-full max-w-3xl">
      <h1 class="text-2xl font-medium mb-6 text-center">Upload Audio for Transcription</h1>
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <input
          type="file"
          multiple
          @change="handleFileChange"
          required
          class="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50 focus:outline-none p-1"
        />
        <button
          type="submit"
          class="w-full bg-pink-500 hover:bg-pink-700 text-white font-medium py-2 px-2 rounded focus:outline-none focus:shadow-outline"
        >
          Transcribe
        </button>
      </form>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex justify-center mt-4">
        <p> transcription...</p>
      </div>


      <!-- Button to Download All Transcriptions -->
      <div v-if="Object.keys(results).length > 1" class="mt-6">
        <button
          @click="downloadAllTranscriptions('txt')"
          class="w-full bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Download All as Text
        </button>
        <button
          @click="downloadAllTranscriptions('srt')"
          class="w-full bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mt-2"
        >
          Download All as SRT
        </button>
        <button
          @click="downloadAllTranscriptions('json')"
          class="w-full bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mt-2"
        >
          Download All as Json
        </button>
      </div>

      <div v-for="(transcription, filename) in results" :key="filename" class="mt-6">
        <h3 class="text-lg font-medium text-gray-800">{{ filename }}</h3>
        <pre class="bg-gray-100 p-4 rounded text-wrap overflow-auto max-h-64">{{ transcription["text"] }}</pre>
        <div class="mt-2 flex space-x-2">
          <button
            @click="downloadTranscription(filename, transcription.text, 'txt')"
            class="bg-indigo-500 hover:bg-indigo-700 text-white font-medium py-1 px-2 rounded focus:outline-none focus:shadow-outline"
          >
            Download as Text
          </button>
          <button
            @click="downloadTranscription(filename, JSON.stringify(transcription.json, null, 2), 'json')"
            class="bg-violet-500 hover:bg-violet-700 text-white font-medium py-1 px-2 rounded focus:outline-none focus:shadow-outline"
          >
            Download as JSON
          </button>
          <button
            @click="downloadTranscription(filename, transcription.srt, 'srt')"
            class="bg-fuchsia-500 hover:bg-fuchsia-700 text-white font-medium py-1 px-2 rounded focus:outline-none focus:shadow-outline"
          >
            Download as SRT
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';


export default {
  setup() {
    const files = ref([]);
    const results = ref({});
    const isLoading = ref(false);

    const handleFileChange = (event) => {
      files.value = event.target.files;
    };

    const handleSubmit = async () => {
      isLoading.value = true;
      const formData = new FormData();
      for (const file of files.value) {
        formData.append('files', file);
      }

      const response = await fetch('http://localhost:8000/transcribe/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      results.value = data;
      isLoading.value = false;
    };

    const downloadTranscription = (filename, content, format) => {
      const blob = new Blob([content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    };

    const downloadAllTranscriptions = async (format) => {
      const zip = new JSZip();
      for (const [filename, transcription] of Object.entries(results.value)) {
        let content;
        if (format === 'txt') {
          content = transcription.text;
        } else if (format === 'srt') {
          content = transcription.srt;
        }
        else if (format === 'json') {
          content = JSON.stringify(transcription.json, null, 2);
        }
        zip.file(`${filename}.${format}`, content);
      }
      const blob = await zip.generateAsync({ type: 'blob' });
      saveAs(blob, `transcriptions_${format}.zip`);
    };

    return {
      handleFileChange,
      handleSubmit,
      downloadTranscription,
      downloadAllTranscriptions,
      results,
      isLoading,
    };
  },
};
</script>

<style>
/* Optionally, you can add additional styles here */
</style>
