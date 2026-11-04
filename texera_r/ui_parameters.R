# This file is part of texera-rudf
#
# Copyright (c) 2024 The Texera Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

function(code) {
  .texera_decode <- function(bytes) {
    text <- rawToChar(as.raw(bytes))
    Encoding(text) <- "UTF-8"
    text
  }

  texera_ui_parameters <- function(script, parameters, attribute_types, resources) {
    .texera_parameters <- parameters
    AttributeType <- attribute_types
    Resource <- resources
    .texera_parse <- function(raw, type, name) {
      invalid <- function() stop(sprintf("Invalid %s value for UiParameter '%s'.", type, name), call.=FALSE)
      if (type == "string") return(raw)
      text <- trimws(raw)
      if (!nzchar(text)) invalid()
      if (type %in% c("boolean", "double") && grepl("^[+-]?0[xX]", text)) invalid()
      if (type == "boolean") {
        if (tolower(text) == "true") return(TRUE)
        if (tolower(text) == "false") return(FALSE)
        result <- suppressWarnings(as.numeric(text))
        if (is.na(result) && !is.nan(result)) invalid()
        return(is.nan(result) || result != 0)
      }
      if (type %in% c("integer", "long")) {
        if (!grepl("^[+-]?[0-9]+$", text)) invalid()
        if (type == "long") {
          if (!requireNamespace("bit64", quietly=TRUE))
            stop("LONG UiParameters require the R package 'bit64'.", call.=FALSE)
          result <- suppressWarnings(bit64::as.integer64(text))
          digits <- sub("^[+-]?0*", "", text)
          canonical <- if (!nzchar(digits)) "0" else
            paste0(if (startsWith(text, "-")) "-" else "", digits)
          # Some bit64 implementations clamp overflow; verify the exact decimal value.
          if (is.na(result) || as.character(result) != canonical) invalid()
          return(result)
        }
        result <- suppressWarnings(as.numeric(text))
        if (is.na(result) || result < -2147483648 || result > 2147483647) invalid()
        # R reserves INT_MIN for NA; keep that boundary exactly as a numeric scalar.
        return(if (result == -2147483648) result else as.integer(result))
      }
      if (type == "double") {
        result <- suppressWarnings(as.numeric(text))
        if (is.na(result) && !is.nan(result)) invalid()
        return(result)
      }
      if (type == "timestamp") {
        if (grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", text)) text <- paste0(text, "T00:00:00")
        zone <- "(Z|[+-][0-9]{2}:?[0-9]{2})?"
        text <- sub(paste0("([T ][0-9]{2})", zone, "$"), "\\1:00:00\\2", text)
        text <- sub(paste0("([T ][0-9]{2}:[0-9]{2})", zone, "$"), "\\1:00\\2", text)
        if (!grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ]([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]+)?(Z|[+-][0-9]{2}:?[0-9]{2})?$", text)) invalid()
        text <- sub(" ", "T", text, fixed=TRUE)
        text <- sub("Z$", "+0000", text)
        text <- sub("([+-][0-9]{2}):([0-9]{2})$", "\\1\\2", text)
        if (!grepl("[+-][0-9]{4}$", text)) text <- paste0(text, "+0000")
        result <- as.POSIXct(strptime(text, format="%Y-%m-%dT%H:%M:%OS%z", tz="UTC"))
        if (is.na(result)) invalid()
        return(result)
      }
      invalid()
    }

    UiParameter <- function(name, type=NULL, value=NULL, attr_type=NULL) {
      if (!is.character(name) || length(name) != 1L || is.na(name) || !nzchar(trimws(name)))
        stop("UiParameter name must be a non-empty string.", call.=FALSE)
      if (!is.null(attr_type)) {
        if (!is.null(type)) stop("UiParameter.type was provided multiple times.", call.=FALSE)
        type <- attr_type
      }
      if (!is.character(type) || length(type) != 1L || is.na(type) || !type %in% unlist(AttributeType))
        stop("UiParameter.type must be a supported AttributeType member.", call.=FALSE)
      if (!is.null(value) && (!is.character(value) || length(value) != 1L || is.na(value) ||
          !value %in% unlist(Resource) || type != "string"))
        stop("UiParameter.value must name a Resource and have type STRING.", call.=FALSE)
      name <- trimws(name)
      parameter <- .texera_parameters[[name]]
      if (is.null(parameter)) stop(sprintf("No UI parameter value found for '%s'.", name), call.=FALSE)
      if (!identical(parameter$type, type) || !identical(parameter$inputType, if (is.null(value)) "" else value))
        stop(sprintf("UiParameter '%s' does not match its saved type or resource.", name), call.=FALSE)
      list(name=name, type=type, value=.texera_parse(parameter$value, type, name), resource=value)
    }
    eval(substitute(script), envir=environment())
  }
  eval(parse(text=code, keep.source=TRUE), envir=environment())
}
