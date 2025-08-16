import React, { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Upload, FileText, AlertCircle, CheckCircle2, X } from "lucide-react"

interface FileUploadProps {
  title: string
  description: string
  expectedColumns: string[]
  onFileUpload: (file: File, data: any[]) => void
  uploadedFile?: File
  validationError?: string
  previewData?: any[]
}

export function FileUpload({ 
  title, 
  description, 
  expectedColumns, 
  onFileUpload, 
  uploadedFile, 
  validationError, 
  previewData 
}: FileUploadProps) {
  const [isDragActive, setIsDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      
      // Parse CSV file
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        const lines = text.split('\n')
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
        
        // Validate headers
        const expectedLower = expectedColumns.map(col => col.toLowerCase())
        const hasAllColumns = expectedLower.every(col => headers.includes(col))
        
        if (!hasAllColumns) {
          onFileUpload(file, [])
          return
        }
        
        // Parse data rows
        const data = lines.slice(1, 6) // First 5 rows for preview
          .filter(line => line.trim())
          .map(line => {
            const values = line.split(',')
            const row: any = {}
            headers.forEach((header, index) => {
              row[header] = values[index]?.trim() || ''
            })
            return row
          })
        
        onFileUpload(file, data)
      }
      reader.readAsText(file)
    }
  }, [expectedColumns, onFileUpload])

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xlsx'],
    },
    multiple: false,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
  })

  const isValid = uploadedFile && !validationError
  const hasError = validationError

  return (
    <Card className={`transition-smooth ${isValid ? 'border-accent shadow-soft' : hasError ? 'border-destructive' : ''}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          {isValid && <CheckCircle2 className="w-6 h-6 text-accent" />}
          {hasError && <AlertCircle className="w-6 h-6 text-destructive" />}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {!uploadedFile && (
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-smooth
              ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}
            `}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto w-12 h-12 text-muted-foreground mb-4" />
            <p className="text-sm font-medium mb-2">
              Drag and drop your file here, or click to select
            </p>
            <p className="text-xs text-muted-foreground">
              CSV or Excel files only
            </p>
          </div>
        )}

        {uploadedFile && (
          <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-primary" />
              <div>
                <p className="text-sm font-medium">{uploadedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(uploadedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.location.reload()}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}

        {validationError && (
          <Alert variant="destructive">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription>{validationError}</AlertDescription>
          </Alert>
        )}

        {previewData && previewData.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Data Preview</h4>
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    {expectedColumns.map(col => (
                      <TableHead key={col} className="text-xs">
                        {col.replace('_', ' ').toUpperCase()}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {previewData.map((row, index) => (
                    <TableRow key={index}>
                      {expectedColumns.map(col => (
                        <TableCell key={col} className="text-xs">
                          {row[col.toLowerCase()] || '-'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}

        <div className="text-xs text-muted-foreground">
          <p className="font-medium mb-1">Expected columns:</p>
          <p>{expectedColumns.join(', ')}</p>
        </div>
      </CardContent>
    </Card>
  )
}