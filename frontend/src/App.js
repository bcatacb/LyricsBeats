import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Progress } from './components/ui/progress';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';
import { Music, Upload, Zap, Mic2, Download, Plus, Trash2, Play, Pause, Volume2 } from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Home/Landing Page Component
const HomePage = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Failed to load projects');
    } finally {
      setIsLoading(false);
    }
  };

  const createProject = async () => {
    const name = prompt('Enter project name:');
    if (!name) return;

    try {
      const response = await axios.post(`${API}/projects`, { name });
      navigate(`/studio/${response.data.id}`);
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-black/50"></div>
        <div className="relative px-6 lg:px-8">
          <div className="mx-auto max-w-7xl pt-20 pb-32 sm:pt-24 sm:pb-40">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl mb-8">
                Transform Beats with <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">AI Magic</span>
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-300 max-w-2xl mx-auto">
                Upload your instrumentals and watch them transform into original beats. Generate custom rap lyrics that match your style. Create copyright-ready music in minutes.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Button onClick={createProject} size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-8 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                  <Plus className="mr-2 h-5 w-5" />
                  Start Creating
                </Button>
                <Button variant="outline" size="lg" className="border-white/20 text-white hover:bg-white/10 py-3 px-8 rounded-full">
                  Learn More
                </Button>
              </div>
            </div>
            
            {/* Feature Images */}
            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 opacity-80">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform duration-300">
                <img src="https://images.unsplash.com/photo-1595598237436-bf64a3bf18cd" alt="Audio Production" className="w-full h-48 object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                <div className="absolute bottom-4 left-4 text-white">
                  <h3 className="font-semibold">Audio Transformation</h3>
                </div>
              </div>
              <div className="relative rounded-2xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform duration-300">
                <img src="https://images.unsplash.com/photo-1583568671741-c75e1e2e4389" alt="Beat Production" className="w-full h-48 object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                <div className="absolute bottom-4 left-4 text-white">
                  <h3 className="font-semibold">Beat Creation</h3>
                </div>
              </div>
              <div className="relative rounded-2xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform duration-300">
                <img src="https://images.unsplash.com/photo-1535406208535-1429839cfd13" alt="Professional Mixing" className="w-full h-48 object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                <div className="absolute bottom-4 left-4 text-white">
                  <h3 className="font-semibold">Professional Quality</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-slate-800/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-gray-300">Everything you need to create original music</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
              <CardContent className="p-6 text-center">
                <Upload className="h-12 w-12 text-purple-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Easy Upload</h3>
                <p className="text-gray-300 text-sm">Upload any instrumental and start transforming</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
              <CardContent className="p-6 text-center">
                <Zap className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">AI Transform</h3>
                <p className="text-gray-300 text-sm">AI-powered beat transformation technology</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
              <CardContent className="p-6 text-center">
                <Mic2 className="h-12 w-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Lyrics AI</h3>
                <p className="text-gray-300 text-sm">Generate custom rap lyrics in any style</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
              <CardContent className="p-6 text-center">
                <Download className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Export Ready</h3>
                <p className="text-gray-300 text-sm">Download copyright-ready final tracks</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="py-16 px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-bold text-white">Recent Projects</h2>
            <Button onClick={createProject} className="bg-purple-600 hover:bg-purple-700">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </div>
          
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
              <p className="text-gray-300 mt-4">Loading projects...</p>
            </div>
          ) : projects.length === 0 ? (
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
              <CardContent className="p-12 text-center">
                <Music className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No projects yet</h3>
                <p className="text-gray-300 mb-6">Create your first project to get started</p>
                <Button onClick={createProject} className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                  <Plus className="mr-2 h-4 w-4" />
                  Create First Project
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <Card key={project.id} className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300 cursor-pointer" onClick={() => navigate(`/studio/${project.id}`)}>
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      {project.name}
                      <Music className="h-5 w-5 text-purple-400" />
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-300">Status:</span>
                        <Badge variant={project.transformed_file ? "default" : "secondary"}>
                          {project.transformed_file ? "Transformed" : "Uploaded"}
                        </Badge>
                      </div>
                      {project.style && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-300">Style:</span>
                          <Badge variant="outline" className="text-purple-300 border-purple-300">
                            {project.style}
                          </Badge>
                        </div>
                      )}
                      <div className="text-xs text-gray-400">
                        Updated: {new Date(project.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Studio Component
const StudioPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [transformProgress, setTransformProgress] = useState(0);
  const [userStyles, setUserStyles] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('trap');
  const [customPrompt, setCustomPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isTransforming, setIsTransforming] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    fetchProject();
    fetchUserStyles();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Error fetching project:', error);
      toast.error('Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUserStyles = async () => {
    try {
      const response = await axios.get(`${API}/user-styles`);
      setUserStyles(response.data);
    } catch (error) {
      console.error('Error fetching user styles:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadProgress(0);
      const response = await axios.post(`${API}/projects/${projectId}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      toast.success('File uploaded successfully!');
      fetchProject();
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Failed to upload file');
    }
  };

  const transformBeat = async () => {
    setIsTransforming(true);
    setTransformProgress(0);
    
    try {
      // Simulate progress
      const interval = setInterval(() => {
        setTransformProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      await axios.post(`${API}/projects/${projectId}/transform`);
      
      clearInterval(interval);
      setTransformProgress(100);
      toast.success('Beat transformed successfully!');
      fetchProject();
    } catch (error) {
      console.error('Error transforming beat:', error);
      toast.error('Failed to transform beat');
    } finally {
      setIsTransforming(false);
      setTransformProgress(0);
    }
  };

  const generateLyrics = async () => {
    setIsGenerating(true);
    
    try {
      const response = await axios.post(`${API}/projects/${projectId}/generate-lyrics`, {
        project_id: projectId,
        style: selectedStyle,
        custom_prompt: customPrompt || undefined,
        user_style_id: selectedStyle === 'custom' ? userStyles[0]?.id : undefined
      });
      
      toast.success('Lyrics generated successfully!');
      fetchProject();
    } catch (error) {
      console.error('Error generating lyrics:', error);
      toast.error('Failed to generate lyrics');
    } finally {
      setIsGenerating(false);
    }
  };

  const exportProject = async () => {
    setIsExporting(true);
    
    try {
      // Get export info
      const exportResponse = await axios.get(`${API}/projects/${projectId}/export`);
      const exportData = exportResponse.data;
      
      if (!exportData.ready_for_export) {
        toast.error('Project not ready for export. Please upload and transform a beat, then generate lyrics.');
        return;
      }
      
      // Download audio file if available
      if (exportData.audio_file) {
        const audioLink = document.createElement('a');
        audioLink.href = `${API}/files/${exportData.audio_file}`;
        audioLink.download = `${exportData.project_name}_beat.mp3`;
        document.body.appendChild(audioLink);
        audioLink.click();
        document.body.removeChild(audioLink);
      }
      
      // Download lyrics file
      if (exportData.has_lyrics) {
        const lyricsResponse = await axios.get(`${API}/projects/${projectId}/download-lyrics`, {
          responseType: 'blob'
        });
        
        const lyricsBlob = new Blob([lyricsResponse.data], { type: 'text/plain' });
        const lyricsUrl = window.URL.createObjectURL(lyricsBlob);
        const lyricsLink = document.createElement('a');
        lyricsLink.href = lyricsUrl;
        lyricsLink.download = `${exportData.project_name}_lyrics.txt`;
        document.body.appendChild(lyricsLink);
        lyricsLink.click();
        document.body.removeChild(lyricsLink);
        window.URL.revokeObjectURL(lyricsUrl);
      }
      
      toast.success('Project exported successfully! Check your downloads folder.');
      
    } catch (error) {
      console.error('Error exporting project:', error);
      toast.error('Failed to export project');
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="text-white mt-4">Loading studio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to="/" className="text-purple-400 hover:text-purple-300 mb-2 inline-block">← Back to Home</Link>
            <h1 className="text-3xl font-bold text-white">{project?.name}</h1>
          </div>
          <div className="flex gap-4">
            <Button 
              onClick={exportProject}
              disabled={isExporting || !project?.transformed_file || !project?.lyrics}
              className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 disabled:opacity-50"
            >
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Export Project
                </>
              )}
            </Button>
          </div>
        </div>

        <Tabs defaultValue="upload" className="space-y-6">
          <TabsList className="bg-white/10 backdrop-blur-sm">
            <TabsTrigger value="upload" className="data-[state=active]:bg-purple-500">Upload & Transform</TabsTrigger>
            <TabsTrigger value="lyrics" className="data-[state=active]:bg-purple-500">Generate Lyrics</TabsTrigger>
            <TabsTrigger value="styles" className="data-[state=active]:bg-purple-500">Manage Styles</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* File Upload */}
              <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Upload className="mr-2 h-5 w-5" />
                    Upload Instrumental
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!project?.original_file ? (
                    <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-purple-400 transition-colors">
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-white mb-2">Drag & drop your instrumental here</p>
                      <p className="text-gray-400 text-sm mb-4">or click to browse files</p>
                      <Input
                        type="file"
                        accept="audio/*"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="file-upload"
                      />
                      <Label htmlFor="file-upload">
                        <Button className="bg-purple-600 hover:bg-purple-700 cursor-pointer" asChild>
                          <span>Choose File</span>
                        </Button>
                      </Label>
                    </div>
                  ) : (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Music className="h-5 w-5 text-green-400 mr-2" />
                          <span className="text-white">File uploaded successfully</span>
                        </div>
                        <Badge className="bg-green-500/20 text-green-300">Ready</Badge>
                      </div>
                    </div>
                  )}
                  
                  {uploadProgress > 0 && uploadProgress < 100 && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-white">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <Progress value={uploadProgress} className="h-2" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Beat Transformation */}
              <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Zap className="mr-2 h-5 w-5" />
                    Transform Beat
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-300 text-sm">
                    Transform your uploaded instrumental into an original beat using AI processing.
                  </p>
                  
                  {project?.transformed_file ? (
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Zap className="h-5 w-5 text-blue-400 mr-2" />
                          <span className="text-white">Beat transformed</span>
                        </div>
                        <Badge className="bg-blue-500/20 text-blue-300">Complete</Badge>
                      </div>
                    </div>
                  ) : (
                    <Button 
                      onClick={transformBeat} 
                      disabled={!project?.original_file || isTransforming}
                      className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                    >
                      {isTransforming ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Transforming...
                        </>
                      ) : (
                        <>
                          <Zap className="mr-2 h-4 w-4" />
                          Transform Beat
                        </>
                      )}
                    </Button>
                  )}
                  
                  {transformProgress > 0 && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-white">
                        <span>Processing...</span>
                        <span>{transformProgress}%</span>
                      </div>
                      <Progress value={transformProgress} className="h-2" />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="lyrics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Lyrics Generation */}
              <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Mic2 className="mr-2 h-5 w-5" />
                    Generate Lyrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-white">Rap Style</Label>
                    <Select value={selectedStyle} onValueChange={setSelectedStyle}>
                      <SelectTrigger className="bg-white/5 border-white/20 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="trap">Trap</SelectItem>
                        <SelectItem value="boom_bap">Boom Bap</SelectItem>
                        <SelectItem value="drill">Drill</SelectItem>
                        <SelectItem value="conscious">Conscious</SelectItem>
                        <SelectItem value="melodic">Melodic</SelectItem>
                        <SelectItem value="freestyle">Freestyle</SelectItem>
                        {userStyles.length > 0 && <SelectItem value="custom">My Custom Style</SelectItem>}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-white">Custom Prompt (Optional)</Label>
                    <Textarea
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="Add specific themes, topics, or requirements..."
                      className="bg-white/5 border-white/20 text-white placeholder:text-gray-400"
                      rows={3}
                    />
                  </div>

                  <Button 
                    onClick={generateLyrics} 
                    disabled={isGenerating}
                    className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <Mic2 className="mr-2 h-4 w-4" />
                        Generate Lyrics
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Generated Lyrics Display */}
              <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white">Generated Lyrics</CardTitle>
                </CardHeader>
                <CardContent>
                  {project?.lyrics ? (
                    <div className="space-y-4">
                      <div className="bg-black/20 rounded-lg p-4 font-mono text-sm text-white whitespace-pre-wrap max-h-80 overflow-y-auto">
                        {project.lyrics}
                      </div>
                      <div className="flex items-center justify-between">
                        <Badge className="bg-purple-500/20 text-purple-300">
                          Style: {project.style}
                        </Badge>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="border-white/20 text-white hover:bg-white/10"
                            onClick={() => navigator.clipboard.writeText(project.lyrics)}
                          >
                            Copy Lyrics
                          </Button>
                          <Button 
                            size="sm" 
                            className="bg-blue-600 hover:bg-blue-700"
                            onClick={async () => {
                              try {
                                const response = await axios.get(`${API}/projects/${projectId}/download-lyrics`, {
                                  responseType: 'blob'
                                });
                                const blob = new Blob([response.data], { type: 'text/plain' });
                                const url = window.URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = `${project.name}_lyrics.txt`;
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                window.URL.revokeObjectURL(url);
                                toast.success('Lyrics downloaded!');
                              } catch (error) {
                                toast.error('Failed to download lyrics');
                              }
                            }}
                          >
                            <Download className="mr-1 h-3 w-3" />
                            Download
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Mic2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-300">No lyrics generated yet</p>
                      <p className="text-gray-400 text-sm">Generate lyrics to see them here</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="styles">
            <UserStylesManager userStyles={userStyles} onStylesChange={fetchUserStyles} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// User Styles Manager Component
const UserStylesManager = ({ userStyles, onStylesChange }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newStyle, setNewStyle] = useState({ name: '', description: '', sample_lyrics: '' });

  const createUserStyle = async () => {
    if (!newStyle.name || !newStyle.description || !newStyle.sample_lyrics) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      await axios.post(`${API}/user-styles`, newStyle);
      toast.success('Style created successfully!');
      setNewStyle({ name: '', description: '', sample_lyrics: '' });
      setIsDialogOpen(false);
      onStylesChange();
    } catch (error) {
      console.error('Error creating style:', error);
      toast.error('Failed to create style');
    }
  };

  const deleteUserStyle = async (styleId) => {
    if (!confirm('Are you sure you want to delete this style?')) return;

    try {
      await axios.delete(`${API}/user-styles/${styleId}`);
      toast.success('Style deleted successfully!');
      onStylesChange();
    } catch (error) {
      console.error('Error deleting style:', error);
      toast.error('Failed to delete style');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Your Custom Styles</h2>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-purple-600 hover:bg-purple-700">
              <Plus className="mr-2 h-4 w-4" />
              Add Style
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-800 border-slate-600">
            <DialogHeader>
              <DialogTitle className="text-white">Create Custom Style</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-white">Style Name</Label>
                <Input
                  value={newStyle.name}
                  onChange={(e) => setNewStyle({...newStyle, name: e.target.value})}
                  placeholder="e.g., My Signature Flow"
                  className="bg-white/5 border-white/20 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-white">Description</Label>
                <Textarea
                  value={newStyle.description}
                  onChange={(e) => setNewStyle({...newStyle, description: e.target.value})}
                  placeholder="Describe your style, flow, and typical themes..."
                  className="bg-white/5 border-white/20 text-white"
                  rows={3}
                />
              </div>
              <div className="space-y-2">
                <Label className="text-white">Sample Lyrics</Label>
                <Textarea
                  value={newStyle.sample_lyrics}
                  onChange={(e) => setNewStyle({...newStyle, sample_lyrics: e.target.value})}
                  placeholder="Paste some of your existing lyrics as examples..."
                  className="bg-white/5 border-white/20 text-white"
                  rows={5}
                />
              </div>
              <Button onClick={createUserStyle} className="w-full bg-purple-600 hover:bg-purple-700">
                Create Style
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {userStyles.length === 0 ? (
        <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <Mic2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No custom styles yet</h3>
            <p className="text-gray-300 mb-6">Create your first custom style by uploading samples of your work</p>
            <Button onClick={() => setIsDialogOpen(true)} className="bg-gradient-to-r from-purple-500 to-pink-500">
              <Plus className="mr-2 h-4 w-4" />
              Create First Style
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {userStyles.map((style) => (
            <Card key={style.id} className="bg-white/5 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  {style.name}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteUserStyle(style.id)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-gray-300 text-sm">{style.description}</p>
                <div className="bg-black/20 rounded p-3 text-xs text-gray-300 max-h-32 overflow-y-auto">
                  {style.sample_lyrics.substring(0, 200)}...
                </div>
                <div className="text-xs text-gray-400">
                  Created: {new Date(style.created_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/studio/:projectId" element={<StudioPage />} />
        </Routes>
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;